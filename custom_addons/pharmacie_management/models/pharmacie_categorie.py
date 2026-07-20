from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PharmacieCategorie(models.Model):
    _name = 'pharmacie.categorie'
    _description = "Catégorie thérapeutique de médicaments"
    _order = 'name'
    _parent_store = True

    name = fields.Char(required=True)
    code = fields.Char()
    description = fields.Text()
    parent_id = fields.Many2one(
        'pharmacie.categorie', string='Catégorie parente',
        ondelete='restrict', index=True)
    child_ids = fields.One2many(
        'pharmacie.categorie', 'parent_id', string='Sous-catégories')
    parent_path = fields.Char(index=True)

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'Le code de la catégorie doit être unique.'),
    ]

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(_("Vous ne pouvez pas créer de catégories récursives."))
