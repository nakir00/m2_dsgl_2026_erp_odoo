from odoo import api, fields, models


class PharmacieMedicament(models.Model):
    _name = 'pharmacie.medicament'
    _description = "Médicament du catalogue"
    _order = 'nom_commercial'
    _rec_name = 'nom_commercial'

    nom_commercial = fields.Char(string="Nom commercial", required=True)
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

    prix_achat = fields.Float(string="Prix d'achat (FCFA)")
    prix_vente = fields.Float(string="Prix de vente (FCFA)")
    taux_tva = fields.Selection(
        [('0', "0 %"), ('18', "18 %")],
        string="Taux de TVA", default='18')
    marge_pct = fields.Float(
        string="Marge (%)", compute='_compute_marge_pct', store=True)

    sur_ordonnance = fields.Boolean(string="Vente sur ordonnance")
    notice = fields.Text(string="Notice")
    photo = fields.Image(string="Photo")

    lot_ids = fields.One2many('pharmacie.lot', 'medicament_id', string="Lots")
    stock_actuel = fields.Float(
        string="Stock actuel", compute='_compute_stock_actuel', store=True)
    alerte_rupture = fields.Integer(
        string="Seuil d'alerte de rupture", default=10)

    @api.depends('prix_achat', 'prix_vente')
    def _compute_marge_pct(self):
        for rec in self:
            if rec.prix_achat:
                rec.marge_pct = (rec.prix_vente - rec.prix_achat) / rec.prix_achat * 100
            else:
                rec.marge_pct = 0.0

    @api.depends('lot_ids.quantite_restante', 'lot_ids.date_peremption')
    def _compute_stock_actuel(self):
        today = fields.Date.context_today(self)
        for rec in self:
            lots_valides = rec.lot_ids.filtered(
                lambda lot: lot.quantite_restante > 0
                and (not lot.date_peremption or lot.date_peremption >= today)
            )
            rec.stock_actuel = sum(lots_valides.mapped('quantite_restante'))
