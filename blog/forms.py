from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, FieldList, FormField, Field, RadioField
from wtforms.validators import DataRequired

import logging

class AnswerField(FlaskForm):
    p_answer = StringField("", default="{{this.p_answer}}", _name="")
    is_correct = BooleanField(default="{{is_correct}}", _name="")



class AnswerRadioField(FlaskForm):
    r_answers = RadioField("")
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField("", validators=[DataRequired()], default="{{title}}")
    body = TextAreaField("", default="{{body}}")
    summary = StringField("", default="{{summary}}")
    tags = StringField("", default="{{tags}}")
    category = StringField("", validators=[DataRequired()], default="{{category}}")
    answers = FieldList(FormField(AnswerField), min_entries=4)
    submit = SubmitField('Save')

