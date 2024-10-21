from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

borrowing_list_schema = extend_schema_view(
    list=extend_schema(
        description=f"Retrieve a list of borrowings and allows filtering by several criteria",
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter borrowings by activity. Example: True",
                required=False,
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter borrowings by user id. Example: 3",
                required=False
            )
        ]
    )
)
