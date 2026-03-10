/**
 * CDK app for the Geometry Art Gallery application.
 * Defines storage (S3), compute (Lambda), API (API Gateway), queue (SQS), and delivery (CloudFront).
 */
import {
  App,
  CfnOutput,
  Duration,
  RemovalPolicy,
  Stack,
  type StackProps,
} from 'aws-cdk-lib'
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment'
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront'
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins'
import * as acm from 'aws-cdk-lib/aws-certificatemanager'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as logs from 'aws-cdk-lib/aws-logs'
import * as iam from 'aws-cdk-lib/aws-iam'
import * as sqs from 'aws-cdk-lib/aws-sqs'
import * as lambda_event_sources from 'aws-cdk-lib/aws-lambda-event-sources'
import { Construct } from 'constructs'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

class GeometryStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)

    // S3 bucket that holds the static web app (HTML, JS, CSS). Served via CloudFront only.
    const webBucket = new s3.Bucket(this, 'WebBucket', {
      bucketName: 'com.martincastroalvarez.geometry',
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.RETAIN,
    })

    // S3 bucket for API data (polygon inputs, job outputs). Lambdas read and write here; CORS for browser uploads.
    const apiBucket = new s3.Bucket(this, 'ApiBucket', {
      bucketName: 'com.martincastroalvarez.api.geometry',
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.RETAIN,
      cors: [
        {
          allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.DELETE],
          allowedOrigins: ['*'],
          allowedHeaders: ['*'],
        },
      ],
    })

    // SQS queue for async polygon optimization jobs. API enqueues; worker Lambda consumes.
    const geometryQueue = new sqs.Queue(this, 'GeometryQueue', {
      queueName: 'geometry-queue',
      visibilityTimeout: Duration.seconds(960),
      receiveMessageWaitTime: Duration.seconds(20),
      retentionPeriod: Duration.days(14),
    })

    // Origin Access Identity so CloudFront can read from the web bucket without making it public.
    const oai = new cloudfront.OriginAccessIdentity(this, 'GeometryOAI', {
      comment: 'OAI for Geometry web application',
    })
    webBucket.grantRead(oai)

    // IAM role for the API Lambda: secrets read, API bucket read/write, and permission to send messages to the queue.
    const lambdaRole = new iam.Role(this, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
    })
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:GetObject'],
      resources: ['arn:aws:s3:::com.martincastroalvarez.secrets/*'],
    }))
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:GetObject', 's3:PutObject', 's3:DeleteObject', 's3:ListBucket'],
      resources: [`${apiBucket.bucketArn}/*`],
    }))
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:ListBucket'],
      resources: [apiBucket.bucketArn],
    }))
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['sqs:SendMessage', 'sqs:GetQueueUrl'],
      resources: [geometryQueue.queueArn],
    }))

    // IAM role for the worker Lambda: secrets, API bucket, and full SQS access to consume and delete messages.
    const workerLambdaRole = new iam.Role(this, 'WorkerLambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
    })
    workerLambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:GetObject'],
      resources: ['arn:aws:s3:::com.martincastroalvarez.secrets/*'],
    }))
    workerLambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:GetObject', 's3:PutObject', 's3:DeleteObject', 's3:ListBucket'],
      resources: [`${apiBucket.bucketArn}/*`, apiBucket.bucketArn],
    }))
    workerLambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['sqs:SendMessage', 'sqs:ReceiveMessage', 'sqs:DeleteMessage', 'sqs:GetQueueAttributes', 'sqs:GetQueueUrl', 'sqs:PurgeQueue'],
      resources: [geometryQueue.queueArn],
    }))

    // API Lambda: handles REST requests (galleries, polygon validation, job CRUD). Enqueues jobs for the worker.
    const apiHandler = new lambda.Function(this, 'GeometryApiHandler', {
      functionName: 'geometry-api-handler',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'api.handler',
      role: lambdaRole,
      code: lambda.Code.fromAsset(join(__dirname, 'api'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c', [
              'pip install --no-cache-dir -r requirements.txt -t /asset-output',
              'cp -r /asset-input/* /asset-output/'
            ].join(' && ')
          ]
        }
      }),
      environment: {
        SECRETS_BUCKET_NAME: 'com.martincastroalvarez.secrets',
        DATA_BUCKET_NAME: apiBucket.bucketName,
        QUEUE_NAME: geometryQueue.queueName,
        LOG_LEVEL: 'WARNING',
      },
      timeout: Duration.seconds(30),
      memorySize: 256,
      logRetention: logs.RetentionDays.ONE_DAY,
    })

    // Worker Lambda: triggered by SQS; runs polygon optimization and writes results to the API bucket.
    const workerHandler = new lambda.Function(this, 'GeometryWorkerHandler', {
      functionName: 'geometry-worker-handler',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'workers.handler',
      role: workerLambdaRole,
      code: lambda.Code.fromAsset(join(__dirname, 'api'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            'bash', '-c', [
              'pip install --no-cache-dir -r requirements.txt -t /asset-output',
              'cp -r /asset-input/* /asset-output/'
            ].join(' && ')
          ]
        }
      }),
      environment: {
        SECRETS_BUCKET_NAME: 'com.martincastroalvarez.secrets',
        DATA_BUCKET_NAME: apiBucket.bucketName,
        QUEUE_NAME: geometryQueue.queueName,
        LOG_LEVEL: 'WARNING',
      },
      timeout: Duration.seconds(900),
      memorySize: 512,
      logRetention: logs.RetentionDays.ONE_DAY,
    })

    // Connect the queue to the worker. Batch size 1 so long-running polygon tasks do not block others; maxConcurrency kept low for cost.
    workerHandler.addEventSource(new lambda_event_sources.SqsEventSource(geometryQueue, {
      batchSize: 1,
      maxBatchingWindow: Duration.seconds(30),
      maxConcurrency: 20,
    }))

    // REST API backed by the API Lambda; access logs, prod stage, CORS so preflight succeeds.
    const api = new apigateway.RestApi(this, 'GeometryApi', {
      restApiName: 'Geometry API',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: apigateway.Cors.DEFAULT_HEADERS.concat(['X-Auth']),
      },
      deployOptions: {
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        stageName: 'prod',
        accessLogDestination: new apigateway.LogGroupLogDestination(
          new logs.LogGroup(this, 'GeometryApiGatewayAccessLogs', {
            retention: logs.RetentionDays.ONE_DAY,
            removalPolicy: RemovalPolicy.DESTROY,
          })
        ),
        accessLogFormat: apigateway.AccessLogFormat.jsonWithStandardFields()
      }
    })

    // TLS certificate for the API custom domain (geometry.api.martincastroalvarez.com).
    const geometryApiCertificate = acm.Certificate.fromCertificateArn(
      this,
      'GeometryApiCertificate',
      'arn:aws:acm:us-west-2:217471729873:certificate/272482bb-5287-4365-a125-1bece4096502'
    )

    // Custom domain and base path mapping so the API is reachable at the chosen hostname.
    const apiDomainName = new apigateway.DomainName(this, 'GeometryApiCustomDomain', {
      domainName: 'geometry.api.martincastroalvarez.com',
      certificate: geometryApiCertificate,
      endpointType: apigateway.EndpointType.REGIONAL,
      securityPolicy: apigateway.SecurityPolicy.TLS_1_2,
    })

    new apigateway.BasePathMapping(this, 'GeometryApiPathMapping', {
      domainName: apiDomainName,
      restApi: api,
    })

    // Throttling and usage plan; allows API Gateway to invoke the Lambda.
    const usagePlan = new apigateway.UsagePlan(this, 'GeometryUsagePlan', {
      name: 'GeometryUsagePlan',
      description: 'Usage plan for Geometry API',
      throttle: {
        rateLimit: 100,
        burstLimit: 20,
      },
    })
    usagePlan.addApiStage({ stage: api.deploymentStage })

    // Allow API Gateway to invoke the API Lambda.
    new lambda.CfnPermission(this, 'GeometryApiGatewayLambdaPermission', {
      action: 'lambda:InvokeFunction',
      functionName: apiHandler.functionName,
      principal: 'apigateway.amazonaws.com',
      sourceArn: `arn:aws:execute-api:${this.region}:${this.account}:${api.restApiId}/*/*/*`
    })

    // All API routes are proxied to the same API Lambda; routing is handled inside the Lambda.
    const lambdaIntegration = new apigateway.LambdaIntegration(apiHandler, {
      allowTestInvoke: true,
      proxy: true
    })

    // API structure: /v1/galleries, /v1/polygon, /v1/jobs, /v1/publish/{id}.
    const v1Resource = api.root.addResource('v1')
    const publishResource = v1Resource.addResource('publish')
    const publishIdResource = publishResource.addResource('{id}')
    publishIdResource.addMethod('POST', lambdaIntegration)

    const galleriesResource = v1Resource.addResource('galleries')
    galleriesResource.addMethod('GET', lambdaIntegration)
    const galleryIdResource = galleriesResource.addResource('{id}')
    galleryIdResource.addMethod('GET', lambdaIntegration)

    const polygonResource = v1Resource.addResource('polygon')
    polygonResource.addMethod('POST', lambdaIntegration)

    const jobsResource = v1Resource.addResource('jobs')
    jobsResource.addMethod('GET', lambdaIntegration)
    jobsResource.addMethod('POST', lambdaIntegration)
    const jobIdResource = jobsResource.addResource('{id}')
    jobIdResource.addMethod('GET', lambdaIntegration)
    jobIdResource.addMethod('POST', lambdaIntegration)
    jobIdResource.addMethod('PATCH', lambdaIntegration)
    jobIdResource.addMethod('DELETE', lambdaIntegration)

    // CloudFront distribution for the web app: S3 origin, HTTPS, SPA fallback for 404/403.
    const distribution = new cloudfront.Distribution(this, 'GeometryDistribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(webBucket, { originAccessIdentity: oai }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        { httpStatus: 404, responseHttpStatus: 200, responsePagePath: '/index.html' },
        { httpStatus: 403, responseHttpStatus: 200, responsePagePath: '/index.html' },
      ],
      domainNames: ['geometry.martincastroalvarez.com'],
      certificate: acm.Certificate.fromCertificateArn(
        this,
        'GeometryWebCertificate',
        'arn:aws:acm:us-east-1:217471729873:certificate/e4280b09-ab4c-4d0c-9adb-33f9b672a8f9'
      )
    })

    // Deploy the built web app from apps/web/dist to the web bucket and invalidate CloudFront.
    new s3deploy.BucketDeployment(this, 'GeometryDeployWebsite', {
      sources: [s3deploy.Source.asset(join(__dirname, 'apps', 'web', 'dist'))],
      destinationBucket: webBucket,
      distribution,
      distributionPaths: ['/*'],
      prune: true,
      retainOnDelete: false,
    })

    // Stack outputs for reference or cross-stack use.
    new CfnOutput(this, 'WebBucketName', { value: webBucket.bucketName, exportName: 'GeometryWebBucketName' })
    new CfnOutput(this, 'ApiBucketName', { value: apiBucket.bucketName, exportName: 'GeometryApiBucketName' })
    new CfnOutput(this, 'GeometryQueueName', { value: geometryQueue.queueName, exportName: 'GeometryQueueName' })
    new CfnOutput(this, 'GeometryQueueUrl', { value: geometryQueue.queueUrl, exportName: 'GeometryQueueUrl' })
    new CfnOutput(this, 'GeometryDistributionId', { value: distribution.distributionId, exportName: 'GeometryDistributionId' })
    new CfnOutput(this, 'GeometryDistributionDomainName', { value: distribution.distributionDomainName, exportName: 'GeometryDistributionDomainName' })
    new CfnOutput(this, 'GeometryApiUrl', { value: api.url, exportName: 'GeometryApiUrl' })
    new CfnOutput(this, 'GeometryApiDomainName', { value: apiDomainName.domainNameAliasDomainName, exportName: 'GeometryApiDomainName' })
    new CfnOutput(this, 'LambdaFunctionName', { value: apiHandler.functionName, exportName: 'GeometryLambdaFunctionName' })
    new CfnOutput(this, 'WorkerFunctionName', { value: workerHandler.functionName, exportName: 'GeometryWorkerFunctionName' })
  }
}

// CDK app entry: single stack in us-west-2 for the Geometry service.
const app = new App()
new GeometryStack(app, 'GeometryStack', {
  env: {
    region: 'us-west-2',
    account: '217471729873',
  },
})
