# Fiche de règles pratiques — Module Odoo 18 Community (`pharmacie_management`)

> Synthèse du *Odoo 19 Development Cookbook* (6e éd., Packt 2026, Daudi/Vora), adaptée à **Odoo 18 Community**.
> Le livre cible Odoo 19 : les points marqués **⚠️ Odoo 19 only** ne doivent PAS être utilisés sur 18 ; l'équivalent 18 est donné à chaque fois.

---

## 1. Structure de module

### Arborescence recommandée

```
pharmacie_management/
├── __init__.py              # from . import models, wizards, controllers
├── __manifest__.py
├── controllers/             # (optionnel) __init__.py + fichiers
├── data/                    # données initiales (séquences, decimal.precision…)
├── demo/                    # données de démo
├── i18n/                    # .pot/.po (pas à déclarer dans le manifest)
├── models/                  # __init__.py + 1 fichier par modèle, nommé comme le modèle
├── reports/                 # ir.actions.report + templates QWeb + paperformats
├── security/                # groups.xml, ir.model.access.csv, record_rules.xml
├── static/description/icon.png   # icône module (PNG)
├── views/                   # 1 fichier XML par modèle + menus.xml
└── wizards/                 # __init__.py + modèles transient + leurs vues
```

### Règles

- Nom technique du module = identifiant Python valide, **minuscules + underscores**.
- 1 fichier Python **par modèle**, nommé d'après le modèle (`pharmacie_medicament.py` pour `pharmacie.medicament`).
- Tout fichier Python doit être importé via les `__init__.py` ; tout fichier XML/CSV doit être listé dans `data` du manifest — sinon il est **silencieusement ignoré**.
- `static/` est le seul dossier au nom imposé : son contenu est public (accessible sans login).

### `__manifest__.py` — clés essentielles

```python
{
    'name': "Gestion de Pharmacie",
    'summary': "Catalogue, lots, ventes comptoir, réapprovisionnement",
    'description': "…",           # ou README.md à la racine du module
    'author': "…",
    'category': 'Inventory',       # sert aussi à générer base.module_category_* pour les groupes
    'version': '18.0.1.0.0',       # TOUJOURS préfixer par la version Odoo cible
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],   # lister TOUT module dont on référence modèles/vues/XML IDs
    'data': [
        'security/groups.xml',           # 1. groupes d'abord
        'security/ir.model.access.csv',  # 2. puis ACL
        'security/record_rules.xml',     # 3. puis règles d'enregistrement
        'data/data.xml',                 # 4. données (séquences, précisions…)
        'views/....xml',                 # 5. vues et menus
        'reports/....xml',               # 6. rapports
        'wizards/....xml',
    ],
    'demo': ['demo/demo.xml'],
    'application': True,           # module central d'un domaine fonctionnel
    'installable': True,
}
```

- **L'ordre de la liste `data` est critique** : un fichier ne peut référencer que des XML IDs déjà chargés (groupes → ACL → vues).
- Installation/màj CLI : `odoo-bin -d db -i pharmacie_management` (install) / `-u pharmacie_management` (upgrade). Tout changement de modèle ou de fichier XML exige une **mise à jour du module**.
- `odoo-bin scaffold mon_module chemin/addons` génère un squelette de départ.

---

## 2. Modèles ORM

### Conventions de nommage

| Élément | Convention | Exemple |
|---|---|---|
| `_name` | `<module_court>.<objet>` avec points | `pharmacie.medicament` |
| Table SQL générée | points → underscores | `pharmacie_medicament` |
| Champ Many2one | suffixe `_id` | `medicament_id` |
| Champ One2many/Many2many | suffixe `_ids` | `lot_ids`, `ligne_ids` |
| Méthode compute | `_compute_<champ>` | `_compute_prix_ttc` |
| Méthode contrainte | `_check_<sujet>` | `_check_marge` |
| Champ Selection état | `state` (+ widget statusbar) | `state = fields.Selection([...])` |

### Attributs structurels du modèle

- `_name` (obligatoire), `_description` (obligatoire sinon **warning** au chargement).
- `_order = "date_vente desc, id desc"` — uniquement des champs **stockés** ; syntaxe type SQL ORDER BY.
- `_rec_name = 'champ'` si le champ d'affichage n'est pas `name`.
- `_rec_names_search = ['name', 'dci', 'code']` — champs cherchés dans les widgets Many2one (remplace un `_name_search` custom simple).
- Affichage composé : surcharger `_compute_display_name` (ex. « Doliprane 500mg (DOL500) ») :
  ```python
  @api.depends('name', 'dosage')
  def _compute_display_name(self):
      for rec in self:
          rec.display_name = f"{rec.name} {rec.dosage or ''}".strip()
  ```
  ⚠️ `name_get()` **n'existe plus** depuis Odoo 17 — ne pas l'utiliser.

### Champs — attributs utiles

- Communs : `string`, `help`, `required`, `readonly`, `default` (valeur **ou callable** : `default=fields.Date.context_today` — ne jamais appeler la fonction : `today()` serait figé au chargement du serveur), `index=True` (M2o souvent), `copy`, `groups='module.group_x'` (vraie sécurité, ORM+RPC), `tracking=True` (nécessite `mail.thread`).
- `active = fields.Boolean(default=True)` → active la fonctionnalité **archiver/désarchiver** ; les enregistrements `active=False` sont filtrés partout. Pour tout voir : `self.env['...'].with_context(active_test=False).search([])`.
- Noms réservés (ne pas redéfinir) : `id`, `create_date`, `create_uid`, `write_date`, `write_uid`.
- ⚠️ **Odoo 18** : l'attribut d'agrégation s'appelle `aggregator="sum"` (le `group_operator` du livre est l'ancien nom, déprécié).
- Précision décimale configurable (utile prix/TVA) : `fields.Float(digits='Product Price')` — la chaîne référence un enregistrement `decimal.precision` (créé en data XML).

### Monétaire

```python
currency_id = fields.Many2one('res.currency', string='Devise',
    default=lambda self: self.env.company.currency_id)
prix_vente = fields.Monetary('Prix de vente')   # cherche currency_id par défaut
```

Si le champ devise a un autre nom : `fields.Monetary(currency_field='autre_devise_id')`.

### Champs relationnels (patterns catalogue/stock/vente)

- **Many2one** : `lot_id = fields.Many2one('pharmacie.lot', ondelete='restrict', index=True)`
  - `ondelete` : `'set null'` (défaut), `'restrict'` (empêche la suppression du parent — bon pour lot→médicament), `'cascade'` (supprime en cascade — bon pour ligne de vente→vente).
  - `domain="[('active','=',True)]"` et `context` : côté client, filtrent les choix.
- **One2many** = miroir d'un Many2one obligatoire dans le co-modèle :
  ```python
  # sur pharmacie.vente :
  ligne_ids = fields.One2many('pharmacie.vente.ligne', 'vente_id', string='Lignes')
  # sur pharmacie.vente.ligne :
  vente_id = fields.Many2one('pharmacie.vente', required=True, ondelete='cascade')
  ```
  Ne crée aucune colonne ; c'est une vue de commodité.
- **Many2many** : table de liaison auto (`model1_model2_rel`) ; donner `relation=` explicite si 2 M2m entre mêmes modèles ou noms > limite PostgreSQL (63 car.).
- **Related** : `dci = fields.Char(related='medicament_id.dci', store=True)` — `store=True` requis pour chercher/trier/grouper dessus. C'est un computed déguisé.

### Champs calculés

```python
prix_ttc = fields.Monetary(compute='_compute_prix_ttc', store=True)
@api.depends('prix_ht', 'tva')
def _compute_prix_ttc(self):
    for rec in self:
        rec.prix_ttc = rec.prix_ht * (1 + rec.tva / 100)
```

- **Toujours assigner une valeur** au champ pour chaque record (sinon erreur) — prévoir la branche `else`.
- Non stocké par défaut → **pas de search/tri/group by** sans `store=True` ou méthode `search=`.
- `store=True` = cache persistant, recalculé automatiquement quand les dépendances (`@api.depends`) changent.
- `inverse='_inverse_x'` rend le champ éditable (écrit dans les dépendances).
- **Onchange moderne** : préférer un champ compute avec `readonly=False` (déclenché aussi côté serveur) à `@api.onchange` (UI uniquement, self en état virtuel `NewId`, **jamais** d'écriture DB dedans).
- `compute_sudo` : défaut `True` si `store=True`, sinon `False`.

### Contraintes

- **Python** (`@api.constrains`) — pour la logique métier, lève `ValidationError` :
  ```python
  from odoo.exceptions import ValidationError
  @api.constrains('date_peremption')
  def _check_peremption(self):
      for rec in self:
          if rec.date_peremption and rec.date_peremption < fields.Date.context_today(rec):
              raise ValidationError(_("La date de péremption est déjà passée."))
  ```
- **SQL** — rapide, fiable (UNIQUE, CHECK). ⚠️ **Odoo 19 only** : `models.Constraint(...)`. **Sur Odoo 18, utiliser** :
  ```python
  _sql_constraints = [
      ('code_uniq', 'UNIQUE(code)', 'Le code médicament doit être unique !'),
      ('marge_positive', 'CHECK(marge >= 0)', 'La marge ne peut pas être négative.'),
  ]
  ```
  Si des lignes existantes violent la contrainte, elle n'est pas ajoutée (erreur dans le log).
- Hiérarchie (catégories) : `parent_id` + `_parent_store = True` + `parent_path = fields.Char(index=True)` ; anti-cycle : `self._has_cycle()` dans un `@api.constrains('parent_id')` (Odoo 18 ; `_check_recursion()` est l'ancien nom).

### Héritage

- **Extension** (le cas courant) : `_inherit = 'model.name'` seul → ajoute champs/méthodes au modèle existant, même table.
- Toujours appeler `super()` en surchargeant une méthode, sinon la chaîne d'héritage est cassée.
- **Abstract** : `models.AbstractModel` pour features réutilisables (ex. `mail.thread`, `mail.activity.mixin`).
- Chatter : `_inherit = ['mail.thread', 'mail.activity.mixin']` + `'mail'` dans depends + `<chatter/>` dans la vue form.

### Logique métier — règles clés

- Méthode sans décorateur : `self` = recordset → **boucler sur self**. `@api.model` : le contenu du recordset est sans importance.
- Erreurs utilisateur : `raise UserError(_("message"))` (`from odoo.exceptions import UserError`) — rollback de la transaction. `ValidationError` pour les contraintes, `AccessError` pour les droits.
- Traduction : `_("texte %s") % val` — jamais `_( "texte %s" % val )`.
- **Surcharge de create sur Odoo 18** : signature batch obligatoire :
  ```python
  @api.model_create_multi
  def create(self, vals_list):
      for vals in vals_list:
          if not vals.get('reference'):
              vals['reference'] = self.env['ir.sequence'].next_by_code('pharmacie.vente')
      return super().create(vals_list)
  ```
  (le `@api.model def create(self, values)` du livre est l'ancien style → warning de dépréciation.)
- Surcharge `write`/`unlink` : contrôles **avant** le `super()` ; attention aux récursions si on ré-écrit après `super()` (poser un marqueur dans le context).
- Écriture O2m/M2m : namespace `Command` (`from odoo import Command`) : `Command.create(vals)`, `Command.link(id)`, `Command.update(id, vals)`, `Command.unlink(id)`, `Command.set(ids)`, `Command.clear()`.
- Autre modèle : `self.env['pharmacie.lot']` → recordset vide ; `.search(domain)`, `.browse(ids)`, `.create(...)`.
- Agrégats (bilan de caisse) : `read_group(domain, ['total:sum'], ['user_id'])` — beaucoup plus rapide que boucler en Python.
- Perf : créer en batch (`create([vals1, vals2])`), écrire une fois sur tout le recordset (`recordset.write(vals)`), jamais de `search`/`write` dans une boucle si évitable.
- `sudo()` avec parcimonie (bypasse ACL + record rules) ; pour tester en tant qu'autre utilisateur : `with_user(user)`.
- ⚠️ **Odoo 18** : `user_has_groups()` n'existe plus → `self.env.user.has_group('module.group_x')`.
- ⚠️ **Odoo 19 only** : `fields.Property()` — sur 18, utiliser `company_dependent=True` sur un champ classique si besoin multi-société.

---

## 3. Vues XML (syntaxe Odoo 18)

### Changements de version à respecter absolument

| Ancien (livres ≤ Odoo 16) | Odoo 18 |
|---|---|
| `<tree>` | **`<list>`** (racine de vue liste) et `view_mode="list,form"` |
| `attrs="{'invisible': [...]}"` / `states="..."` | **expressions directes** : `invisible="state != 'draft'"`, `readonly="not lot_id"`, `required="avec_ordonnance"` (supprimés depuis 17 — erreur au chargement) |
| `name_get()` | `_compute_display_name` |
| `<div class="oe_chatter">…` | **`<chatter/>`** |
| kanban `t-name="kanban-box"` | kanban **`t-name="card"`** |
| `t-esc` dans QWeb | **`t-out`** (t-esc encore toléré mais déprécié) |

### Action + menu (pattern standard)

```xml
<record id="action_medicament" model="ir.actions.act_window">
    <field name="name">Médicaments</field>
    <field name="res_model">pharmacie.medicament</field>
    <field name="view_mode">list,form</field>
    <field name="context">{'search_default_actif': 1}</field>
    <field name="help" type="html"><p class="o_view_nocontent_smiling_face">Créer un médicament</p></field>
</record>
<menuitem id="menu_pharmacie_root" name="Pharmacie" sequence="10"
          web_icon="pharmacie_management,static/description/icon.png"/>
<menuitem id="menu_catalogue" name="Catalogue" parent="menu_pharmacie_root" sequence="10"/>
<menuitem id="menu_medicament" parent="menu_catalogue" action="action_medicament"
          groups="pharmacie_management.group_pharmacie_vendeur" sequence="10"/>
```

- Pour lier des vues précises à une action : champ `view_id` (1re vue) ou enregistrements `ir.actions.act_window.view` (contrôle fin par mode).
- Context d'action : `default_<champ>` (valeurs par défaut), `search_default_<nom_filtre>` (filtre pré-activé), `active_test`.
- Action de wizard : `<field name="target">new</field>` (popup).

### Vue form « document » (bonnes pratiques)

```xml
<form>
    <header>
        <button name="action_confirmer" string="Confirmer" type="object"
                class="btn-primary" invisible="state != 'draft'"/>
        <button name="action_annuler" string="Annuler" type="object"
                invisible="state not in ('draft','confirme')"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,confirme,paye"/>
    </header>
    <sheet>
        <div class="oe_button_box" name="button_box">
            <button class="oe_stat_button" type="object" name="action_voir_lots" icon="fa-cubes">
                <field string="Lots" name="lots_count" widget="statinfo"/>
            </button>
        </div>
        <widget name="web_ribbon" title="Archivé" bg_color="bg-danger" invisible="active"/>
        <div class="oe_title"><h1><field name="name" placeholder="Nom"/></h1></div>
        <group>
            <group name="infos_gauche"><field name="dci"/><field name="dosage"/></group>
            <group name="infos_droite"><field name="tva"/><field name="prix_vente"/></group>
        </group>
        <notebook>
            <page string="Lots" name="lots"><field name="lot_ids"/></page>
        </notebook>
    </sheet>
    <chatter/>
</form>
```

- `type="object"` = appelle une méthode Python ; `type="action"` = `name="%(module.action_xml_id)d"`.
- Le clic sur un bouton **sauvegarde d'abord** l'enregistrement.
- Donner un `name` unique aux `<group>`/pages : facilite l'héritage de vue (ne jamais cibler par `string`, cassé par les traductions).
- Stat button : compteur via champ compute + `search_count`, contexte `{'search_default_medicament_id': active_id}` sur l'action cible pour filtrer.

### Vue list

```xml
<list decoration-danger="date_peremption and date_peremption &lt; current_date"
      decoration-muted="quantite == 0" default_order="date_peremption">
    <field name="name"/>
    <field name="quantite" sum="Total"/>
    <field name="date_peremption" optional="show"/>
    <field name="state" optional="hide"/>
</list>
```

- `decoration-{bf,it,danger,warning,success,info,muted,primary}="expr"` ; `sum`/`avg`/`min`/`max` sur colonnes numériques ; `optional="show|hide"` ; `editable="bottom"` pour édition inline (lignes de vente embarquées) ; widget `handle` sur un champ `sequence` pour le drag & drop.
- Tri : seulement sur champs stockés (related/compute → `store=True`).

### Vue search

```xml
<search>
    <field name="name" filter_domain="['|', ('name','ilike',self), ('dci','ilike',self)]"/>
    <filter name="perimes" string="Périmés"
            domain="[('date_peremption','&lt;', context_today().strftime('%Y-%m-%d'))]"/>
    <separator/>
    <filter name="avec_ordonnance" string="Avec ordonnance" domain="[('ordonnance','=',True)]"/>
    <group expand="0" string="Regrouper par">
        <filter name="group_state" string="État" context="{'group_by': 'state'}"/>
    </group>
    <searchpanel>
        <field name="categorie_id" icon="fa-filter" enable_counters="1"/>
    </searchpanel>
</search>
```

- **Échapper `<` en XML** : `&lt;`.
- Filtres d'un même `<group>`/entre `<separator/>` combinés en OR, sinon AND.

### Domaines

- Format : liste de triplets `('champ', 'op', valeur)` ; préfixes `&` (défaut), `|`, `!` ; chemins pointés autorisés (`'lot_id.medicament_id.dci'`).
- Opérateurs : `=, !=, in, not in, <, <=, >, >=, like, ilike, =like, =ilike, child_of, =?`.
- Piège : `('m2m_ids.name', '!=', 'X')` a une sémantique « il existe une ligne liée ≠ X », pas « aucune ligne = X ».
- Combiner des domaines par code : `odoo.osv.expression.AND / OR` (ne pas bricoler à la main).

### Héritage de vue

```xml
<record id="view_form_inherit_x" model="ir.ui.view">
    <field name="model">pharmacie.medicament</field>
    <field name="inherit_id" ref="pharmacie_management.view_medicament_form"/>
    <field name="arch" type="xml">
        <xpath expr="//group[@name='infos_gauche']" position="inside">
            <field name="nouveau_champ"/>
        </xpath>
        <field name="tva" position="attributes">
            <attribute name="readonly">state != 'draft'</attribute>
        </field>
    </field>
</record>
```

- `position` : `inside` (défaut), `before`, `after`, `replace` (à éviter — casse les autres héritages), `attributes`, `move`.
- Raccourci : `<field name="x" position="after">…</field>` cible directement un champ unique.
- Ordre d'application : champ `priority` croissant ; hériter d'une vue héritante pour forcer un ordre.

### Kanban (Odoo 18)

```xml
<kanban default_group_by="state" sample="1">
    <field name="name"/>
    <templates>
        <t t-name="card">
            <div class="fw-bold"><field name="name"/></div>
            <field name="quantite"/>
        </t>
    </templates>
</kanban>
```

- `default_group_by` = colonnes drag & drop (changement d'état par glisser-déposer) ; options `quick_create`, `group_create`, `archivable`.

---

## 4. Sécurité

### Groupes (`security/groups.xml`) — syntaxe **Odoo 18**

⚠️ Le livre (Odoo 19) utilise `res.groups.privilege` + `privilege_id` : **n'existe pas sur 18**. Sur 18 :

```xml
<odoo>
    <record id="module_category_pharmacie" model="ir.module.category">
        <field name="name">Pharmacie</field>
        <field name="sequence">30</field>
    </record>
    <record id="group_pharmacie_vendeur" model="res.groups">
        <field name="name">Vendeur</field>
        <field name="category_id" ref="module_category_pharmacie"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>
    <record id="group_pharmacie_pharmacien" model="res.groups">
        <field name="name">Pharmacien</field>
        <field name="category_id" ref="module_category_pharmacie"/>
        <field name="implied_ids" eval="[(4, ref('group_pharmacie_vendeur'))]"/>
    </record>
    <record id="group_pharmacie_gestionnaire" model="res.groups">
        <field name="name">Gestionnaire</field>
        <field name="category_id" ref="module_category_pharmacie"/>
        <field name="implied_ids" eval="[(4, ref('group_pharmacie_pharmacien'))]"/>
        <field name="user_ids" eval="[(4, ref('base.user_admin'))]"/>
    </record>
</odoo>
```

- `implied_ids` en chaîne linéaire dans la même catégorie → affiché comme **liste déroulante** sur la fiche utilisateur (vendeur < pharmacien < gestionnaire).
- Les droits sont **cumulatifs** : on ne peut jamais retirer un droit via un groupe, seulement en ajouter.
- Assigner l'admin au groupe le plus élevé (`user_ids`), sinon même l'admin ne voit pas les menus.

### ACL (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_medicament_vendeur,pharmacie.medicament.vendeur,model_pharmacie_medicament,group_pharmacie_vendeur,1,0,0,0
access_medicament_gestionnaire,pharmacie.medicament.gestionnaire,model_pharmacie_medicament,group_pharmacie_gestionnaire,1,1,1,1
```

- Nom de fichier **imposé** : `ir.model.access.csv`.
- `model_id:id` = `model_<nom_modele_avec_underscores>` (préfixer `module.` si le modèle vient d'un autre module).
- Convention id : `access_<modele>_<groupe>`.
- **Depuis Odoo 12, aucun accès par défaut** : sans ACL, ni menus ni vues ne s'affichent (même pour l'admin, sauf mode superuser) + warning au chargement.
- **Chaque modèle** (y compris chaque wizard TransientModel, obligatoire depuis Odoo 14) doit avoir sa ligne ACL.

### Record rules (`security/record_rules.xml`)

```xml
<odoo noupdate="1">
    <!-- Le vendeur ne voit que SES ventes -->
    <record id="rule_vente_vendeur" model="ir.rule">
        <field name="name">Vente : ses propres ventes</field>
        <field name="model_id" ref="model_pharmacie_vente"/>
        <field name="groups" eval="[(4, ref('group_pharmacie_vendeur'))]"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
    </record>
    <!-- Le gestionnaire voit tout -->
    <record id="rule_vente_gestionnaire" model="ir.rule">
        <field name="name">Vente : toutes</field>
        <field name="model_id" ref="model_pharmacie_vente"/>
        <field name="groups" eval="[(4, ref('group_pharmacie_gestionnaire'))]"/>
        <field name="domain_force">[(1, '=', 1)]</field>
    </record>
</odoo>
```

- Toujours dans `<odoo noupdate="1">` (personnalisations client préservées à l'upgrade).
- Variable `user` disponible à droite du domaine (`user.id`, `user.company_id.id`) ; notation pointée OK à gauche.
- Règles **avec groupe** = combinées en **OR** (additives) ; règles **sans groupe** = globales, combinées en **AND** (restrictives, non contournables).
- Un groupe parent hérite des restrictions → donner explicitement `[(1,'=',1)]` au groupe manager.
- Les record rules sont **ignorées en mode superuser** → tester avec un vrai utilisateur de chaque profil.
- Champs de perm sur la règle : `perm_read/write/create/unlink` (défaut : tous cochés).

### Visibilité fine

- `groups='module.group_x'` **sur le champ Python** = vraie sécurité (ORM + RPC + UI).
- `groups="module.group_x"` **dans le XML** (`<field>`, `<button>`, `<menuitem>`, `<group>`, `<header>`…) = cosmétique uniquement (contournable par RPC).
- `invisible/readonly/required` dans les vues = UX, pas de la sécurité ; doubler par des contrôles dans `create/write` ou `@api.constrains` si l'enjeu est réel.

---

## 5. Wizards (TransientModel)

### Règles générales

- `models.TransientModel` : table réelle mais purgée périodiquement ; **ACL obligatoires** ; interdiction de One2many vers un modèle persistant (utiliser Many2many).
- Fichiers dans `wizards/`, modèle nommé p.ex. `pharmacie.reappro.wizard`, vue + action dans `wizards/*.xml`.
- Action : `ir.actions.act_window` avec `target="new"` (dialogue). Vue form avec `<footer>` :
  ```xml
  <footer>
      <button string="Valider" name="action_valider" type="object" class="btn-primary"/>
      <button string="Annuler" special="cancel" class="btn-secondary"/>
  </footer>
  ```
- Contexte auto fourni au wizard : `active_model`, `active_id`, `active_ids` (sélection en vue liste), `active_domain` → à exploiter dans les valeurs par défaut (`default=lambda self: self.env.context.get('active_id')`) ou dans la méthode du bouton.
- Retour de la méthode bouton : rien → le dialogue se ferme ; ou retourner un dict d'action (`ir.actions.act_window`, `ir.actions.report`…) pour rediriger/enchaîner (wizard multi-étapes = retourner une action qui ré-affiche le wizard).

### Pattern 1 — wizard de traitement en masse (réappro automatique)

```python
class ReapproWizard(models.TransientModel):
    _name = 'pharmacie.reappro.wizard'
    _description = "Réapprovisionnement automatique"
    fournisseur_id = fields.Many2one('res.partner', required=True)
    seuil = fields.Integer(default=10)
    def action_generer_commandes(self):
        medicaments = self.env['pharmacie.medicament'].browse(
            self.env.context.get('active_ids', []))
        # ou : self.env['pharmacie.medicament'].search([('stock','<', self.seuil)])
        lignes = [Command.create({'medicament_id': m.id, 'quantite': self.seuil - m.stock})
                  for m in medicaments if m.stock < self.seuil]
        if not lignes:
            raise UserError(_("Aucun médicament sous le seuil."))
        commande = self.env['pharmacie.commande'].create({
            'fournisseur_id': self.fournisseur_id.id,
            'ligne_ids': lignes,
        })
        return commande.get_formview_action()   # redirige vers la commande créée
```

- Pour agir sur une sélection multiple depuis la vue liste : `binding_model_id` + `binding_view_types="list"` sur l'action, ou menu Action contextuel.

### Pattern 2 — wizard de calcul/rapport (bilan de caisse)

```python
class BilanCaisseWizard(models.TransientModel):
    _name = 'pharmacie.bilan.caisse.wizard'
    _description = "Bilan de caisse"
    date_debut = fields.Date(required=True, default=fields.Date.context_today)
    date_fin = fields.Date(required=True, default=fields.Date.context_today)
    def action_imprimer(self):
        data = {'date_debut': self.date_debut, 'date_fin': self.date_fin}
        ventes = self.env['pharmacie.vente'].search([
            ('date', '>=', self.date_debut), ('date', '<=', self.date_fin),
            ('state', '=', 'paye')])
        return self.env.ref(
            'pharmacie_management.action_report_bilan_caisse'
        ).report_action(ventes, data=data)
```

- Les agrégats (total par vendeur, par mode de paiement) : `read_group()` dans le wizard ou dans le modèle de rapport.
- Pour injecter des valeurs calculées dans le template : modèle abstrait `report.<module>.<template_id>` avec `_get_report_values(self, docids, data)` retournant `{'doc_ids':…, 'doc_model':…, 'docs':…, 'data': data, …}`.

---

## 6. Rapports PDF (QWeb)

### Déclaration (`reports/xxx_report.xml`) — via `<record>`, le tag `<report>` est obsolète

```xml
<record id="action_report_ticket" model="ir.actions.report">
    <field name="name">Ticket de caisse</field>
    <field name="model">pharmacie.vente</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">pharmacie_management.report_ticket_template</field>
    <field name="report_file">pharmacie_management.report_ticket_template</field>
    <field name="binding_model_id" ref="model_pharmacie_vente"/>  <!-- menu Imprimer -->
    <field name="binding_type">report</field>
    <field name="paperformat_id" ref="paperformat_ticket"/>
</record>
```

- `report_name` = **XML ID complet du template** (`module.template_id`) — sinon échec de génération.
- `qweb-pdf` nécessite **wkhtmltopdf** installé + `web.base.url` accessible (sinon rendu lent/cassé) ; `qweb-html` pour debug dans le navigateur.

### Template — squelette obligatoire

```xml
<template id="report_ticket_template">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">   <!-- ou web.internal_layout -->
                <div class="page">
                    <!-- contenu -->
                </div>
            </t>
        </t>
    </t>
</template>
```

- `web.html_container` + boucle sur `docs` (= recordsets, gère l'impression multiple) sont **indispensables**.
- `web.external_layout` = en-tête/pied avec logo et infos société ; `web.internal_layout` = minimal (pagination, date, société). Toujours utiliser l'un des deux.
- Tout le contenu dans un élément `class="page"` (sinon page blanche).
- Directives : `t-out` (échappé — remplace `t-esc`), `t-field="doc.date"` (formatage auto par type ; options : `t-options="{'widget': 'monetary', 'display_currency': doc.currency_id}"`), `t-foreach/t-as`, `t-if`, `t-set`.
- Sauts de page CSS : `page-break-before/after/inside` ; attribut `groups=` utilisable dans les templates.

### Ticket de caisse (petit format)

- Créer un **paperformat** dédié :
  ```xml
  <record id="paperformat_ticket" model="report.paperformat">
      <field name="name">Ticket 80mm</field>
      <field name="format">custom</field>
      <field name="page_width">80</field>
      <field name="page_height">200</field>
      <field name="margin_top">3</field>
      <field name="margin_bottom">3</field>
      <field name="margin_left">3</field>
      <field name="margin_right">3</field>
      <field name="dpi">80</field>
  </record>
  ```
- Utiliser `web.basic_layout` (aucun habillage société) ou `internal_layout` ; petite typo (`style="font-size:10px"`), lignes article/qté/prix en tableau étroit, total en gras, mentions TVA en bas.

### Document tabulaire (inventaire, bon de commande)

- `<table class="table table-sm">` + `<thead>` répété automatiquement à chaque page par wkhtmltopdf ; aligner les nombres à droite (`class="text-end"`).
- Ligne de totaux : `<t t-set="total" t-value="sum(doc.ligne_ids.mapped('sous_total'))"/>`.
- Grouper par catégorie : boucler sur un dict préparé dans `_get_report_values` ou via `t-foreach` sur `doc.ligne_ids.mapped('categorie_id')`.

---

## 7. Pièges courants Odoo 18 (checklist anti-erreurs)

**Syntaxe supprimée/renommée (erreurs immédiates si on copie de vieux tutos) :**

1. `<tree>` → `<list>` ; `view_mode="tree,form"` → `"list,form"`.
2. `attrs=` et `states=` dans les vues → **supprimés depuis 17** : expressions directes `invisible="state != 'draft'"`.
3. `name_get()` → `_compute_display_name`.
4. `@api.multi` / `@api.one` → n'existent plus (aucun décorateur = méthode recordset).
5. `user_has_groups()` → `self.env.user.has_group()`.
6. `group_operator=` → `aggregator=`.
7. Kanban `t-name="kanban-box"` → `t-name="card"`.
8. `t-esc` → `t-out` ; tag `<report>` → `<record model="ir.actions.report">`.
9. À l'inverse, **ne pas copier du Odoo 19** : `models.Constraint` (→ `_sql_constraints`), `res.groups.privilege`/`privilege_id` (→ `category_id`), `fields.Property()`.

**Erreurs de débutant classiques :**

10. Fichier XML non listé dans `data` du manifest, ou `.py` non importé dans `__init__.py` → silencieusement ignoré.
11. Mauvais ordre dans `data` : groupes avant ACL, ACL avant vues/menus qui les référencent.
12. Pas d'ACL sur un nouveau modèle (y compris **chaque wizard**) → menus invisibles, warning au log ; ne pas développer en mode superuser en permanence (il masque les problèmes de droits ET ignore les record rules).
13. Oublier `_description` → warning ; oublier `default=True` sur `active` → tous les nouveaux enregistrements invisibles.
14. `default=fields.Date.today()` (appelé, figé) au lieu de `default=fields.Date.context_today` (callable).
15. Méthode compute qui n'assigne pas de valeur dans toutes les branches → erreur.
16. Chercher/trier/grouper sur un champ compute ou related **non stocké** → impossible sans `store=True` ou `search=`.
17. Surcharge sans `super()` → chaîne d'héritage cassée ; `create` surchargé sans `@api.model_create_multi`.
18. Écriture DB dans un `@api.onchange` → interdit (record virtuel `NewId`).
19. `<` non échappé dans un domaine XML → erreur de parsing (`&lt;`).
20. `_("msg %s" % val)` → traduction cassée ; interpoler **après** `_()`.
21. `ir.model.access.csv` mal nommé → non importé (le nom de fichier = nom du modèle cible).
22. `Datetime` stocké en **UTC** : conversions d'affichage automatiques, mais comparaisons manuelles à faire avec `fields.Date.context_today(rec)` / `fields.Datetime.context_timestamp`.
23. Boucles de `write`/`create` unitaires → privilégier batch (`create(liste)`, `recordset.write`), `read_group` pour les stats.
24. Oublier `depends: ['mail']` quand on utilise chatter/activités/`tracking=True`.
25. Après tout changement de modèle ou de vue : **mettre à jour le module** (`-u`) — un simple restart ne recharge pas les XML.
