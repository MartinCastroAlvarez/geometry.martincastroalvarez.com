class ArtGalleryError(Exception):
    pass


class IntervalInvalidError(ArtGalleryError):
    pass


class MatrixEmptyError(ArtGalleryError):
    pass


class MatrixDimensionError(ArtGalleryError):
    pass


class MatrixNotSquareError(ArtGalleryError):
    pass


class BoxInvalidEdgeError(ArtGalleryError):
    pass


class PolygonTooFewPointsError(ArtGalleryError):
    pass


class PolygonNotSimpleError(ArtGalleryError):
    pass


class PolygonDegenerateError(ArtGalleryError):
    pass


class ConvexComponentInvalidPolygonError(ArtGalleryError):
    pass


class ConvexComponentNotConvexError(ArtGalleryError):
    pass


class ConvexComponentNotCCWError(ArtGalleryError):
    pass


class ComponentsNoSharedEdgeError(ArtGalleryError):
    pass


class ComponentsEmptyOutsideBoundaryError(ArtGalleryError):
    pass


class ConvexComponentSequenceSubtractionError(ArtGalleryError):
    pass


class ConvexComponentSequenceSubtractionEmptyError(ArtGalleryError):
    pass


class ConvexComponentMergeError(ArtGalleryError):
    pass


class PointInvalidCoordinatesError(ArtGalleryError):
    pass


class CentroidEmptySequenceError(ArtGalleryError):
    pass


class SequenceInvalidPointsError(ArtGalleryError):
    pass


class SequenceInvalidSliceError(ArtGalleryError):
    pass


class SequencePointNotFoundError(ArtGalleryError):
    pass


class SequenceShiftValidationError(ArtGalleryError):
    pass


class StitchWinnerSubsequenceError(ArtGalleryError):
    pass


class SegmentInvalidPointsError(ArtGalleryError):
    pass


class SegmentSequenceInvalidItemsError(ArtGalleryError):
    pass


class EarClippingFailureError(ArtGalleryError):
    pass


class EarClippingSizeError(ArtGalleryError):
    pass


class BridgeFailureError(ArtGalleryError):
    pass


class GuardCoverageFailureError(ArtGalleryError):
    pass


class GuardInvalidPositionError(ArtGalleryError):
    pass


class MatrixInvalidPointsError(ArtGalleryError):
    pass


class ModelMapInvalidDataError(ArtGalleryError):
    pass


class ModelMapKeyError(ArtGalleryError):
    pass


class DesignerInvalidArtGalleryError(ArtGalleryError):
    pass


class ConvexComponentMergeTooManyPointsError(ArtGalleryError):
    pass


class ComponentMergeError(ArtGalleryError):
    pass
