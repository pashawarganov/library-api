from rest_framework import serializers

from book.models import Book
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


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
        )
        read_only_fields = (
            "borrow_date",
            "user",
        )

    def validate(self, attrs):
        book = attrs["book"]

        if book.inventory == 0:
            raise serializers.ValidationError(
                "This book is not currently available for borrowing."
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        return Borrowing.objects.create(user=user, **validated_data)
