# Rapport d'avancement - Projet ERP Odoo M2 DSGL 2026

**Projet :** Gestion de Pharmacie
**Module Odoo :** `pharmacie_management`
**Depot GitHub :** <https://github.com/nakir00/m2_dsgl_2026_erp_odoo>
**GitHub Project :** <https://github.com/users/nakir00/projects/1>
**Date de redaction :** 14 aout 2026
**Branche :** `main`
**Dernier commit observe :** `4ee94ee fix: store all four bilan de caisse compute fields consistently`

## 1. Contexte du travail

Le projet consiste a realiser un module Odoo 18 Community pour la gestion d'une pharmacie dans le cadre de l'examen ERP Odoo du M2 DSGL 2026. Le sujet demande un module fonctionnel, installe dans une structure Odoo propre, avec un rapport technique final.

Le travail realise jusqu'ici couvre trois axes :

- la mise en place du depot GitHub, du suivi projet et des conventions de travail ;
- la preparation d'un environnement local Odoo 18 avec Docker Compose ;
- l'implementation progressive du module `pharmacie_management`.

## 2. Documents et supports analyses

Plusieurs documents de cours et supports projet ont ete utilises pour cadrer le travail :

- guide d'utilisation de Codex avec GitHub Issues, GitHub Projects et MCP ;
- supports Odoo 18 et exemples de structure de module ;
- documents d'installation Odoo sur Ubuntu, utilises comme reference mais non retenus comme mode principal d'execution ;
- supports DNS-LDAP et Keycloak, gardes comme contexte pour d'eventuelles extensions d'infrastructure ;
- sujet officiel `Projet ERP Odoo M2 DSGL.pdf`, qui a fixe le perimetre final du module.

La decision technique principale a ete de rester sur Docker Compose pour le projet de base. Une simulation de deploiement avec K3s ou k3d reste une piste possible pour la partie deploiement, sans imposer VirtualBox.

## 3. Mise en place GitHub et pilotage projet

Le depot GitHub a ete initialise puis structure pour travailler avec une methode simple basee sur GitHub :

- creation du `README.md` principal ;
- creation de `AGENTS.md` pour documenter les consignes de collaboration avec Codex ;
- creation de `docs/github-workflow.md` pour decrire le flux Issues, Project, branches et pull requests ;
- ajout de templates GitHub pour les bugs, fonctionnalites, taches et pull requests ;
- ajout d'un fichier de labels GitHub dans `.github/labels.yml` ;
- rattachement du travail au GitHub Project public `examen erp odoo dsgl 2026`.

Un backlog de 74 issues a ete cree dans le GitHub Project. Les tickets couvrent notamment :

- l'initialisation du projet ;
- la configuration Docker Compose ;
- le catalogue medicaments ;
- la gestion des lots, stocks, peremptions et ruptures ;
- les ventes et ordonnances ;
- le reapprovisionnement fournisseur ;
- la securite par roles ;
- les wizards ;
- les rapports QWeb ;
- les donnees de demonstration ;
- la documentation, les tests et les sujets de deploiement.

Un workflow GitHub Actions a aussi ete ajoute dans `.github/workflows/project-sync.yml`. Son objectif est de deplacer automatiquement les issues liees vers `Done` lorsqu'une issue est fermee ou lorsqu'une pull request mergee ferme des tickets.

## 4. Environnement local Odoo 18

L'environnement local a ete prepare avec Docker Compose, afin d'eviter une installation systeme complexe sur Ubuntu et de garder un demarrage reproductible pour tous les membres de l'equipe.

Fichiers principaux :

- `docker-compose.yml` : orchestration Odoo 18 et PostgreSQL 15 ;
- `odoo/odoo.conf` : configuration Odoo ;
- image officielle `odoo:18` : serveur Odoo sans image locale supplementaire ;
- `custom_addons/` : repertoire des modules specifiques du projet ;
- `docs/docker-compose.md` : guide de demarrage local.

Le seul port publie par defaut est Odoo : `http://localhost:8072`. PostgreSQL reste interne au reseau Docker et possede un healthcheck verifie avant le demarrage d'Odoo.

Commandes utiles :

```bash
docker compose up -d
docker compose logs -f odoo
docker compose down
```

## 5. Configuration VS Code

Des recommandations VS Code ont ete ajoutees pour harmoniser l'environnement de developpement :

- `.vscode/extensions.json` pour les extensions recommandees ;
- `.vscode/settings.json` pour les reglages d'espace de travail ;
- `docs/vscode.md` pour expliquer le role de chaque extension.

Les extensions recommandees couvrent Python, Pylance, Odoo, XML, YAML, Docker, GitHub Pull Requests et Markdownlint. Les extensions Kubernetes et EditorConfig ont ete retirees car elles ne correspondent pas au perimetre Docker Compose retenu.

## 6. Module `pharmacie_management`

Le module Odoo a ete cree dans :

```text
custom_addons/pharmacie_management/
```

Il contient les dossiers standards d'un module Odoo :

- `models/` pour les modeles metier ;
- `views/` pour les vues liste, formulaire, recherche, kanban et menus ;
- `security/` pour les groupes, ACL et record rules ;
- `wizards/` pour les assistants ;
- `report/` pour les rapports QWeb ;
- `data/` pour les sequences ;
- `demo/` pour les donnees de demonstration.

Le fichier `__manifest__.py` decrit le module sous le nom fonctionnel "Gestion de Pharmacie", avec la version `18.0.1.1.0`, la licence `LGPL-3`, et les dependances directes `base` et `web`.

## 7. Fonctionnalites implementees

### Catalogue medicaments

Le modele `pharmacie.medicament` permet de gerer :

- le nom commercial ;
- la DCI ;
- la forme pharmaceutique ;
- le dosage ;
- le conditionnement ;
- la categorie ;
- le fournisseur habituel ;
- le prix d'achat ;
- le prix de vente ;
- le taux de TVA ;
- la marge calculee ;
- l'indication de vente sur ordonnance ;
- la notice et l'image.

Le stock actuel est calcule a partir des lots associes. Une alerte de rupture est aussi prevue.

### Categories

Le modele `pharmacie.categorie` permet de classer les medicaments. Une hierarchie parent-enfant a ete ajoutee, avec controle anti-cycle et contrainte d'unicite du code.

### Fournisseurs

Le modele Odoo standard `res.partner` a ete etendu pour identifier les fournisseurs pharmaceutiques. Les champs ajoutes permettent de stocker le delai moyen de livraison et le numero d'agrement.

### Lots et stocks

Le modele `pharmacie.lot` gere :

- le numero de lot genere automatiquement ;
- le medicament associe ;
- les dates de fabrication, reception et peremption ;
- la quantite initiale ;
- la quantite restante ;
- le prix d'achat du lot ;
- le statut du lot.

Des controles verifient la coherence des dates. Le module calcule aussi le nombre de jours avant peremption et le statut du lot : valide, expire ou epuise.

### Ordonnances et posologies

Le modele `pharmacie.ordonnance` permet de gerer :

- les informations patient ;
- le medecin prescripteur ;
- la structure de sante ;
- la date de prescription ;
- les medicaments prescrits ;
- les posologies ;
- le statut ;
- la vente associee ;
- le scan de l'ordonnance.

Le modele `pharmacie.posologie` complete cette partie avec les instructions de prise par medicament.

### Ventes

Le modele `pharmacie.vente` gere les ventes au comptoir avec ou sans ordonnance. Il inclut :

- une reference de vente ;
- le client ;
- le vendeur ;
- l'ordonnance associee ;
- le statut ;
- le mode de paiement ;
- la date de vente ;
- les lignes de vente ;
- les montants HT, TVA et TTC.

Le modele `pharmacie.vente.ligne` gere les medicaments vendus, les lots utilises, les quantites et les montants calcules.

La confirmation d'une vente decremente les stocks des lots. L'annulation d'une vente restaure les quantites. Une regle empeche la vente d'un medicament soumis a ordonnance si aucune ordonnance n'est associee.

### Reapprovisionnement

Le modele `pharmacie.reappro` gere les commandes fournisseurs :

- reference ;
- fournisseur ;
- date de commande ;
- date de livraison prevue ;
- statut ;
- lignes de commande ;
- montant total.

Le modele `pharmacie.reappro.ligne` gere les medicaments commandes, les quantites, les prix unitaires et les montants.

Le workflow de reapprovisionnement permet de passer une commande et de receptionner les produits. Un assistant de reception partielle cree un lot par livraison avec le numero fournisseur et les dates de fabrication, reception et peremption. Les quantites recues et restantes sont calculees depuis les lots, une sur-reception est bloquee, et le statut passe de `recue_partiellement` a `recue` lorsque le bon est complet.

## 8. Assistants, rapports et donnees de demonstration

Trois wizards ont ete ajoutes :

- `pharmacie.reappro.auto.wizard` pour proposer automatiquement des reapprovisionnements ;
- `pharmacie.reappro.reception.wizard` pour tracer les receptions fournisseur partielles ;
- `pharmacie.bilan.caisse.wizard` pour calculer et imprimer un bilan de caisse sur une periode.

Quatre rapports QWeb PDF ont ete ajoutes :

- ticket de caisse ;
- inventaire de stock ;
- bilan de caisse ;
- bon de commande fournisseur.

Les donnees de demonstration couvrent :

- les medicaments et categories ;
- les fournisseurs pharmaceutiques ;
- les lots ;
- les ordonnances ;
- les ventes confirmees.

Ces donnees servent a presenter rapidement le comportement du module apres installation.

## 9. Securite et droits d'acces

Les groupes demandes par le sujet ont ete crees :

- Vendeur ;
- Pharmacien ;
- Gestionnaire.

Les ACL ont ete alignees avec le tableau de droits du sujet. Des record rules ont ete ajoutees pour limiter certains acces, notamment la consultation des ventes par les vendeurs. Les menus d'administration sont limites aux roles Pharmacien et Gestionnaire. La validation d'une reception fournisseur est reservee au Gestionnaire, y compris cote serveur.

## 10. Interfaces Odoo

Les vues principales ont ete ajoutees pour les objets metier :

- medicaments ;
- lots ;
- ordonnances ;
- ventes ;
- reapprovisionnements ;
- fournisseurs pharmaceutiques.

Le menu principal "Pharmacie" a ete structure pour suivre le perimetre fonctionnel du sujet : catalogue, stock, caisse, ordonnances, achats, assistants et rapports.

## 11. Documentation technique ajoutee

En plus du code, plusieurs documents d'accompagnement ont ete crees :

- `docs/github-workflow.md` : organisation GitHub ;
- `docs/docker-compose.md` : demarrage local ;
- `docs/vscode.md` : environnement VS Code ;
- `docs/fiche-regles-odoo18.md` : rappel des regles pratiques Odoo 18 adaptees au module.

La fiche Odoo 18 documente notamment les conventions de module, l'ordre de chargement du manifest, les changements de syntaxe XML en Odoo 18, les modeles ORM, les contraintes, les vues, les menus et les rapports QWeb.

## 12. Correctifs deja appliques

Plusieurs correctifs ont ete effectues pendant l'implementation :

- correction du champ Odoo `res.groups.users` ;
- retrait d'un attribut XML invalide `editable="false"` ;
- correction d'une expression de date dans les donnees de demonstration ;
- alignement de `compute_sudo` sur les champs du wizard de bilan de caisse ;
- stockage coherent des champs calcules du bilan de caisse.
- correction de la borne de fin du bilan de caisse afin d'inclure les ventes jusqu'a 23:59:59 ;
- ajout des tests Odoo pour le bilan, la reception partielle, la sur-reception, la tracabilite et les droits ;
- ajout du workflow `.github/workflows/odoo-check.yml` pour valider Compose et installer le module en CI.

Ces corrections montrent que le module a deja passe plusieurs cycles de lecture, correction et stabilisation.

## 13. Etat d'avancement par rapport au sujet

| Exigence du sujet | Etat actuel |
| --- | --- |
| Module Odoo 18 Community `pharmacie_management` | Realise |
| Catalogue medicaments | Realise |
| Gestion DCI, forme, dosage, TVA, marge, fournisseur | Realise |
| Gestion des lots et dates de peremption | Realise |
| Alertes rupture et peremption | Realise |
| Ventes avec ou sans ordonnance | Realise |
| Scan d'ordonnance | Realise |
| Reapprovisionnement fournisseur avec reception partielle tracable | Realise |
| Profils Vendeur, Pharmacien, Gestionnaire | Realise |
| Wizard de reapprovisionnement automatique | Realise |
| Wizard de bilan de caisse | Realise |
| Rapports QWeb demandes | Realise |
| Donnees de demonstration | Realise |
| Documentation d'installation locale | Realise |
| Rapport technique final avec UML, captures et repartition | A finaliser |
| Tests Odoo cibles et installation isolee | Realise |
| Validation complete dans Odoo avec captures d'ecran | A finaliser |
| Simulation de deploiement K3s/k3d | Hors perimetre de la demonstration Docker Compose |

## 14. Commits significatifs

Les commits suivants representent les grandes etapes du travail :

- `2134689 chore: initialize github workflow` : initialisation du depot et du workflow GitHub ;
- `20c2fa8 chore: add odoo docker compose workspace` : ajout de l'environnement Docker Compose ;
- `8bbbad9 feat: auto-move linked issues to Done on close/merge` : automatisation GitHub Project ;
- `d6448c0 chore: create pharmacie_management module skeleton` : creation du squelette du module ;
- `5e4b974 feat: create pharmacie_management module manifest` : creation du manifest ;
- `feddf50 feat: create pharmacie.medicament model` : modele medicament ;
- `743267f feat: create pharmacie.lot model` : modele lot ;
- `dc07352 feat: create pharmacie.ordonnance model` : modele ordonnance ;
- `f2770f0 feat: create pharmacie.vente model` : modele vente ;
- `0d365bc feat: create pharmacie.reappro model` : modele reapprovisionnement ;
- `e645afc security: declare Vendeur/Pharmacien/Gestionnaire groups` : groupes de securite ;
- `908caa9 feat: add medicament form/kanban/search views and Stock menu` : interfaces medicaments et stock ;
- `eb579c6 feat: add automatic reappro wizard` : assistant de reapprovisionnement automatique ;
- `97da9a1 feat: add bilan de caisse wizard` : assistant de bilan de caisse ;
- `a204028 feat: add ticket de caisse QWeb PDF report` : rapport ticket de caisse ;
- `51a1544 feat: add stock inventory QWeb PDF report` : rapport inventaire ;
- `4b85d8b feat: add bilan de caisse QWeb PDF report` : rapport bilan de caisse ;
- `f411522 feat: add supplier purchase order QWeb PDF report` : rapport bon de commande ;
- `9300d60 data: add demo lots, ordonnances, and confirmed ventes` : donnees de demonstration operationnelles.

## 15. Points d'attention

Le code et la structure sont en place, mais certains points doivent encore etre verifies avant le rendu final :

- installer ou mettre a jour le module dans une base Odoo propre ;
- verifier les vues dans l'interface Odoo ;
- generer les rapports PDF depuis l'interface ;
- tester les workflows de vente, annulation et reapprovisionnement ;
- confirmer visuellement le scenario de reception partielle puis capturer les ecrans associes ;
- verifier les droits avec des utilisateurs reels appartenant aux groupes Vendeur, Pharmacien et Gestionnaire ;
- produire les captures d'ecran necessaires au rapport final ;
- ajouter les diagrammes UML demandes par le sujet ;
- documenter la repartition du travail entre les membres de l'equipe ;
- documenter la repartition reelle du travail entre les membres de l'equipe.

## 16. Prochaines etapes recommandees

1. Lancer l'environnement Docker Compose.
2. Installer le module `pharmacie_management` dans Odoo.
3. Charger les donnees de demonstration.
4. Realiser une recette fonctionnelle complete avec les roles metier.
5. Capturer les ecrans principaux, dont la reception partielle et les lots generes.
6. Mettre a jour les issues du GitHub Project selon l'etat reel.
7. Completer le rapport technique final avec les captures, UML et la repartition du travail.

## 17. Conclusion

Le projet dispose maintenant d'une base solide : le depot est structure, le suivi GitHub est en place, l'environnement Docker Compose est prepare, et le module Odoo `pharmacie_management` couvre deja l'essentiel du cahier des charges fonctionnel.

La suite du travail doit surtout porter sur la validation dans Odoo, la preparation du rapport technique final et la production des preuves de fonctionnement attendues pour l'examen.
