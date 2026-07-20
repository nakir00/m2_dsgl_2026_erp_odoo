from odoo import fields, models


class PharmacieCategorie(models.Model):
    _name = 'pharmacie.categorie'
    _description = "Catégorie thérapeutique de médicaments"
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char()
    description = fields.Text()

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Le code de la catégorie doit être unique.'),
    ]
