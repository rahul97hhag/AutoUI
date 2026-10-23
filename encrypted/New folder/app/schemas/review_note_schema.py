from app.extensions import ma
from app.models.review_note import ReviewNote


class ReviewNoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReviewNote
        load_instance = True


review_note_schema = ReviewNoteSchema()
review_notes_schema = ReviewNoteSchema(many=True)
