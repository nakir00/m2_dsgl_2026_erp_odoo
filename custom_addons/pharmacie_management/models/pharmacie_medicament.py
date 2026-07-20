from odoo import api, fields, models


class PharmacieMedicament(models.Model):
    _name = 'pharmacie.medicament'
    _description = "Médicament du catalogue"
    _order = 'name'

    name = fields.Char(string="Nom commercial", required=True)
    dci = fields.Char(string="DCI", help="Dénomination Commune Internationale")
    forme = fields.Selection(
        [
            ('comprime', "Comprimé"),
            ('gelule', "Gélule"),
            ('sirop', "Sirop"),
            ('injectable', "Injectable"),
            ('pommade', "Pommade"),
            ('poudre', "Poudre"),
            ('suppositoire', "Suppositoire"),
            ('autre', "Autre"),
        ],
        string="Forme galénique")
    dosage = fields.Char(string="Dosage")
    conditionnement = fields.Char(string="Conditionnement")
    categorie_id = fields.Many2one('pharmacie.categorie', string="Catégorie")
    fournisseur_id = fields.Many2one(
        'res.partner', string="Fournisseur",
        domain="[('is_fournisseur_pharma', '=', True)]")

    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        default=lambda self: self.env.company.currency_id)
    prix_achat = fields.Monetary(string="Prix d'achat")
    prix_vente = fields.Monetary(string="Prix de vente")
    tva = fields.Float(string="TVA (%)")
    marge_pct = fields.Float(
        string="Marge (%)", compute='_compute_marge_pct', store=True)

    sur_ordonnance = fields.Boolean(string="Vente sur ordonnance")
    notice = fields.Text(string="Notice")
    photo = fields.Image(string="Photo")

    @api.depends('prix_achat', 'prix_vente')
    def _compute_marge_pct(self):
        for rec in self:
            if rec.prix_achat:
                rec.marge_pct = (rec.prix_vente - rec.prix_achat) / rec.prix_achat * 100
            else:
                rec.marge_pct = 0.0
