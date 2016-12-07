# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import ChoiceField, Form, ValidationError
from django.test import SimpleTestCase, ignore_warnings

from . import FormFieldAssertionsMixin


class ChoiceFieldTest(FormFieldAssertionsMixin, SimpleTestCase):

    def test_choicefield_1(self):
        f = ChoiceField(choices=[('1', 'One'), ('2', 'Two')])
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual('1', f.clean(1))
        self.assertEqual('1', f.clean('1'))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')

    def test_choicefield_2(self):
        f = ChoiceField(choices=[('1', 'One'), ('2', 'Two')], required=False)
        self.assertEqual('', f.clean(''))
        self.assertEqual('', f.clean(None))
        self.assertEqual('1', f.clean(1))
        self.assertEqual('1', f.clean('1'))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('3')

    def test_choicefield_3(self):
        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')])
        self.assertEqual('J', f.clean('J'))
        msg = "'Select a valid choice. John is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('John')

    def test_choicefield_4(self):
        f = ChoiceField(
            choices=[
                ('Numbers', (('1', 'One'), ('2', 'Two'))),
                ('Letters', (('3', 'A'), ('4', 'B'))), ('5', 'Other'),
            ]
        )
        self.assertEqual('1', f.clean(1))
        self.assertEqual('1', f.clean('1'))
        self.assertEqual('3', f.clean(3))
        self.assertEqual('3', f.clean('3'))
        self.assertEqual('5', f.clean(5))
        self.assertEqual('5', f.clean('5'))
        msg = "'Select a valid choice. 6 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('6')

    def test_choicefield_callable(self):
        def choices():
            return [('J', 'John'), ('P', 'Paul')]
        f = ChoiceField(choices=choices)
        self.assertEqual('J', f.clean('J'))

    def test_choicefield_callable_may_evaluate_to_different_values(self):
        choices = []

        def choices_as_callable():
            return choices

        class ChoiceFieldForm(Form):
            choicefield = ChoiceField(choices=choices_as_callable)

        choices = [('J', 'John')]
        form = ChoiceFieldForm()
        self.assertEqual([('J', 'John')], list(form.fields['choicefield'].choices))

        choices = [('P', 'Paul')]
        form = ChoiceFieldForm()
        self.assertEqual([('P', 'Paul')], list(form.fields['choicefield'].choices))

    def test_choicefield_disabled(self):
        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')], disabled=True)
        self.assertWidgetRendersTo(
            f,
            '<select id="id_f" name="f" disabled><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_doesnt_render_required_when_impossible_to_select_empty_field(self):
        self.assertWidgetRendersTo(
            ChoiceField(choices=[('J', 'John'), ('P', 'Paul')]),
            '<select id="id_f" name="f"><option value="J">John</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_renders_required_when_possible_to_select_empty_field_str(self):
        self.assertWidgetRendersTo(
            ChoiceField(choices=[('', 'select please'), ('P', 'Paul')]),
            '<select id="id_f" name="f" required><option selected value="">select please</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_renders_required_when_possible_to_select_empty_field_list(self):
        self.assertWidgetRendersTo(
            ChoiceField(choices=[['', 'select please'], ['P', 'Paul']]),
            '<select id="id_f" name="f" required><option selected value="">select please</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_renders_required_when_possible_to_select_empty_field_none(self):
        self.assertWidgetRendersTo(
            ChoiceField(choices=[(None, 'select please'), ('P', 'Paul')]),
            '<select id="id_f" name="f" required><option selected value="">select please</option>'
            '<option value="P">Paul</option></select>'
        )

    def test_doesnt_render_required_when_no_choices_are_available(self):
        self.assertWidgetRendersTo(ChoiceField(choices=[]), '<select id="id_f" name="f"></select>')

    @ignore_warnings(category=UnicodeWarning)
    def test_utf8_bytesrings(self):
        # Choice validation with UTF-8 bytestrings as input (these are the
        # Russian abbreviations "мес." and "шт.".
        f = ChoiceField(
            choices=(
                (b'\xd0\xbc\xd0\xb5\xd1\x81.', b'\xd0\xbc\xd0\xb5\xd1\x81.'),
                (b'\xd1\x88\xd1\x82.', b'\xd1\x88\xd1\x82.'),
            ),
        )
        self.assertEqual(f.clean('\u0448\u0442.'), '\u0448\u0442.')
        self.assertEqual(f.clean(b'\xd1\x88\xd1\x82.'), '\u0448\u0442.')
