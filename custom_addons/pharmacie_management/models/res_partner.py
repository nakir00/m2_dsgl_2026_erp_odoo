from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_fournisseur_pharma = fields.Boolean(string="Fournisseur pharmaceutique")
    delai_livraison_moyen = fields.Integer(string="Délai de livraison moyen (jours)")
    numero_agrement = fields.Char(string="Numéro d'agrément")
