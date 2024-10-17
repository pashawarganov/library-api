from rest_framework import serializers

from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.CharField(source="book.title", read_only=True)
    author = serializers.CharField(source="book.author", read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "author",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = serializers.CharField(source="book.title")
    author = serializers.CharField(source="book.author")
    cover = serializers.CharField(source="book.cover")
    daily_fee = serializers.IntegerField(source="book.daily_fee")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "author",
            "cover",
            "borrow_date",
            "daily_fee",
            "expected_return_date",
            "actual_return_date",
        )
