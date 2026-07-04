import enum


class PostVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class LikeTargetType(str, enum.Enum):
    POST = "post"
    COMMENT = "comment"
