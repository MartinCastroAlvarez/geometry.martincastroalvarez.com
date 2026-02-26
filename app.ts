import * as cdk from 'aws-cdk-lib'
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

class GeometryStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    const webBucket = new s3.Bucket(this, 'WebBucket', {
      bucketName: 'com.martincastroalvarez.geometry',
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    })

    const apiBucket = new s3.Bucket(this, 'ApiBucket', {
      bucketName: 'com.martincastroalvarez.api.geometry',
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      cors: [
        {
          allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.DELETE],
          allowedOrigins: ['*'],
          allowedHeaders: ['*'],
        },
      ],
    })

    const geometryQueue = new sqs.Queue(this, 'GeometryQueue', {
      queueName: 'geometry-queue',
      visibilityTimeout: cdk.Duration.seconds(960),
      receiveMessageWaitTime: cdk.Duration.seconds(20),
      retentionPeriod: cdk.Duration.days(14),
    })

    const oai = new cloudfront.OriginAccessIdentity(this, 'GeometryOAI', {
      comment: 'OAI for Geometry web application',
    })
    webBucket.grantRead(oai)

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
        LOG_LEVEL: 'INFO',
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      logRetention: logs.RetentionDays.ONE_DAY,
    })

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
        LOG_LEVEL: 'INFO',
      },
      timeout: cdk.Duration.seconds(900),
      memorySize: 512,
      logRetention: logs.RetentionDays.ONE_DAY,
    })

    workerHandler.addEventSource(new lambda_event_sources.SqsEventSource(geometryQueue, {
      batchSize: 3,
      maxBatchingWindow: cdk.Duration.seconds(300),
      maxConcurrency: 2,
    }))

    const api = new apigateway.RestApi(this, 'GeometryApi', {
      restApiName: 'Geometry API',
      deployOptions: {
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        stageName: 'prod',
        accessLogDestination: new apigateway.LogGroupLogDestination(
          new logs.LogGroup(this, 'GeometryApiGatewayAccessLogs', {
            retention: logs.RetentionDays.ONE_DAY,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
          })
        ),
        accessLogFormat: apigateway.AccessLogFormat.jsonWithStandardFields()
      }
    })

    const geometryApiCertificate = acm.Certificate.fromCertificateArn(
      this,
      'GeometryApiCertificate',
      'arn:aws:acm:us-west-2:217471729873:certificate/272482bb-5287-4365-a125-1bece4096502'
    )

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

    const usagePlan = new apigateway.UsagePlan(this, 'GeometryUsagePlan', {
      name: 'GeometryUsagePlan',
      description: 'Usage plan for Geometry API',
      throttle: {
        rateLimit: 100,
        burstLimit: 20,
      },
    })
    usagePlan.addApiStage({ stage: api.deploymentStage })

    new lambda.CfnPermission(this, 'GeometryApiGatewayLambdaPermission', {
      action: 'lambda:InvokeFunction',
      functionName: apiHandler.functionName,
      principal: 'apigateway.amazonaws.com',
      sourceArn: `arn:aws:execute-api:${this.region}:${this.account}:${api.restApiId}/*/*/*`
    })

    const lambdaIntegration = new apigateway.LambdaIntegration(apiHandler, {
      allowTestInvoke: true,
      proxy: true
    })

    const v1Resource = api.root.addResource('v1')
    const galleriesResource = v1Resource.addResource('galleries')
    galleriesResource.addMethod('GET', lambdaIntegration)
    galleriesResource.addMethod('OPTIONS', lambdaIntegration)
    const galleryIdResource = galleriesResource.addResource('{id}')
    galleryIdResource.addMethod('GET', lambdaIntegration)
    galleryIdResource.addMethod('OPTIONS', lambdaIntegration)

    const jobsResource = v1Resource.addResource('jobs')
    jobsResource.addMethod('GET', lambdaIntegration)
    jobsResource.addMethod('POST', lambdaIntegration)
    jobsResource.addMethod('OPTIONS', lambdaIntegration)
    const jobIdResource = jobsResource.addResource('{id}')
    jobIdResource.addMethod('GET', lambdaIntegration)
    jobIdResource.addMethod('POST', lambdaIntegration)
    jobIdResource.addMethod('OPTIONS', lambdaIntegration)

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

    new s3deploy.BucketDeployment(this, 'GeometryDeployWebsite', {
      sources: [s3deploy.Source.asset(join(__dirname, 'apps', 'web', 'dist'))],
      destinationBucket: webBucket,
      distribution,
      distributionPaths: ['/*'],
      prune: true,
      retainOnDelete: false,
    })

    new cdk.CfnOutput(this, 'WebBucketName', { value: webBucket.bucketName, exportName: 'GeometryWebBucketName' })
    new cdk.CfnOutput(this, 'ApiBucketName', { value: apiBucket.bucketName, exportName: 'GeometryApiBucketName' })
    new cdk.CfnOutput(this, 'GeometryQueueName', { value: geometryQueue.queueName, exportName: 'GeometryQueueName' })
    new cdk.CfnOutput(this, 'GeometryQueueUrl', { value: geometryQueue.queueUrl, exportName: 'GeometryQueueUrl' })
    new cdk.CfnOutput(this, 'GeometryDistributionId', { value: distribution.distributionId, exportName: 'GeometryDistributionId' })
    new cdk.CfnOutput(this, 'GeometryDistributionDomainName', { value: distribution.distributionDomainName, exportName: 'GeometryDistributionDomainName' })
    new cdk.CfnOutput(this, 'GeometryApiUrl', { value: api.url, exportName: 'GeometryApiUrl' })
    new cdk.CfnOutput(this, 'GeometryApiDomainName', { value: apiDomainName.domainNameAliasDomainName, exportName: 'GeometryApiDomainName' })
    new cdk.CfnOutput(this, 'LambdaFunctionName', { value: apiHandler.functionName, exportName: 'GeometryLambdaFunctionName' })
    new cdk.CfnOutput(this, 'WorkerFunctionName', { value: workerHandler.functionName, exportName: 'GeometryWorkerFunctionName' })
  }
}

const app = new cdk.App()
new GeometryStack(app, 'GeometryStack', {
  env: {
    region: 'us-west-2',
    account: '217471729873',
  },
})
