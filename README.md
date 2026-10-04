# Educartable pour Home Assistant (non officiel)

Intégration en **lecture seule** pour le portail **Educartable Familles** (école primaire).
Projet indépendant, sans lien avec Edumoov. L'API utilisée n'est pas documentée : elle peut changer sans préavis.

## Capteurs
- **Devoirs à venir** : nombre de devoirs à partir d'aujourd'hui, détail dans l'attribut `devoirs`.
- **Messages et infos** : derniers éléments du carnet de liaison / infos / événements, détail dans l'attribut `messages`.
- **Enfants** : enfants rattachés au compte (prénom, classe, niveau, enseignant).

Mise à jour toutes les 30 minutes.

## Installation (HACS)
1. HACS → ⋮ → *Dépôts personnalisés* → ajouter l'URL de ce dépôt (catégorie *Intégration*).
2. Installer **Educartable**, puis redémarrer Home Assistant.
3. *Paramètres → Appareils et services → Ajouter une intégration → Educartable*.
4. Saisir l'e-mail et le mot de passe du compte Educartable Familles.

## Limites connues
- Connexion par e-mail et mot de passe uniquement (pas de connexion via un fournisseur tiers).
- Les identifiants sont stockés dans la configuration de Home Assistant.
- Les devoirs et messages sont ceux du compte, sans filtre par enfant.

## Vie privée
Les capteurs contiennent des données scolaires d'enfants : ne partagez pas de captures d'écran ni de journaux contenant ces attributs.
