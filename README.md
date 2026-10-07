<p align="center">
  <img src="docs/educartable-636.png" alt="Logo Educartable" width="200">
</p>

<p align="center">
  <img src="custom_components/educartable/brand/icon@2x.png" alt="Educartable pour Home Assistant" width="120">
</p>

<h1 align="center">Educartable pour Home Assistant</h1>

<p align="center">
  Les messages de l'école et les devoirs de ton enfant, directement dans Home Assistant,<br>
  avec une notification sur ton téléphone dès que l'enseignant publie quelque chose.
</p>

<p align="center">
  <a href="https://ko-fi.com/tillbart"><img alt="Offrez-moi un café" src="https://img.shields.io/badge/☕_Offrez--moi_un_café-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white"></a>
</p>

---

## Pourquoi ce projet ?

Je m'appelle Jérôme. Je travaille dans la GTB et la domotique, et je suis papa d'un enfant en école primaire.

L'école de mon fils utilise **Educartable Familles** pour le carnet de liaison et le cahier de textes. Mon problème : je ne reçois pas les notifications de l'application, et je passe donc à côté des messages de l'enseignant. Comme j'ai déjà Home Assistant à la maison, je me suis dit que la maison pouvait me prévenir toute seule.

Il n'existait aucune intégration, alors j'ai créé celle-ci. Les infos de la scolarité arrivent dans mon tableau de bord, je reçois une notification sur mon téléphone à chaque nouveau message, et on peut aller plus loin avec des automatisations : chez moi, quand j'ouvre la porte en rentrant, l'enceinte me lit directement le message de l'école.

Je la partage au cas où elle servirait à d'autres parents.

> **Projet indépendant et non officiel.** Il n'a aucun lien avec Edumoov, l'éditeur d'Educartable. « Educartable » est le nom de leur service. Le logo Educartable en haut de cette page appartient à son éditeur et n'est affiché que pour identifier le service. L'icône de cette intégration est une création originale.

## Ce que tu obtiens

Trois capteurs, mis à jour toutes les 30 minutes :

| Capteur | Contenu |
|---|---|
| **Devoirs à venir** | Nombre de devoirs à partir d'aujourd'hui. Détail (date, matière, titre, contenu) dans l'attribut `devoirs`. |
| **Messages et infos** | Derniers messages du carnet de liaison, infos et événements de l'école (10 maximum). Détail dans l'attribut `messages`. |
| **Enfants** | Prénom, classe, niveau et enseignant de chaque enfant rattaché au compte. |

Les devoirs et les messages n'apparaissent que si l'enseignant les publie dans Educartable.

## Les possibilités

- **Plusieurs enfants** : si ton compte Educartable Familles regroupe plusieurs enfants (comme dans l'application), le capteur **Enfants** les liste tous, avec leur classe et leur enseignant. Les devoirs et messages des classes de tes enfants arrivent ensemble, sans filtre par enfant pour l'instant.
- **Notification sur le téléphone** dès qu'un nouveau message de l'école est publié, avec le texte dedans. Tu peux l'envoyer à plusieurs téléphones, par exemple ceux des deux parents.
- **Un clic sur la notification** peut ouvrir directement la page des messages d'Educartable pour lire le message en entier.
- **Un tableau de bord** : une simple carte Markdown affiche les devoirs et les derniers messages dans Home Assistant.
- **Une annonce vocale** : quand quelqu'un rentre le soir (porte d'entrée, présence), une enceinte connectée peut lire les devoirs à faire.
- **Tes propres automatisations** : les capteurs sont de simples entités Home Assistant, tu peux les utiliser dans des scènes, des conditions ou des scripts.

Je n'ai testé l'intégration qu'avec un seul enfant : si tu en as plusieurs et que quelque chose ne s'affiche pas comme prévu, ouvre une *issue* pour me le dire.

## Installation avec HACS

1. Dans HACS, clique sur les trois points en haut à droite, puis **Dépôts personnalisés**.
2. Colle l'adresse de ce dépôt, choisis le type **Intégration**, puis **Ajouter**.
3. Cherche **Educartable** dans HACS et clique sur **Télécharger**.
4. Redémarre Home Assistant.
5. Va dans **Paramètres → Appareils et services → Ajouter une intégration → Educartable**.
6. Saisis l'e-mail et le mot de passe de ton compte Educartable Familles.

L'icône personnalisée demande Home Assistant 2026.3 ou plus récent.

## Exemple : une notification à chaque nouveau message

Dans **Paramètres → Automatisations et scènes → Créer une automatisation → ⋮ → Modifier en YAML**, colle ce texte en remplaçant `TON_TELEPHONE` par le nom de ton application mobile (cherche `mobile_app` dans Outils de développement → Actions) :

```yaml
alias: Educartable - nouveau message
description: Notification téléphone quand l'école publie un nouveau message
triggers:
  - trigger: state
    entity_id: sensor.educartable_messages_et_infos
conditions:
  - condition: template
    value_template: >
      {{ trigger.from_state is not none
         and trigger.from_state.state not in ['unavailable', 'unknown']
         and trigger.to_state.state not in ['unavailable', 'unknown'] }}
  - condition: template
    value_template: >
      {% set avant = (trigger.from_state.attributes.messages or []) | sort(attribute='date') | list %}
      {% set apres = (trigger.to_state.attributes.messages or []) | sort(attribute='date') | list %}
      {{ apres | length > 0 and (avant | length == 0
         or avant[-1].date != apres[-1].date
         or avant[-1].titre != apres[-1].titre) }}
actions:
  - action: notify.mobile_app_TON_TELEPHONE
    data:
      title: >
        École : {{ (state_attr('sensor.educartable_messages_et_infos','messages') | sort(attribute='date') | list)[-1].titre }}
      message: >
        {% set m = (state_attr('sensor.educartable_messages_et_infos','messages') | sort(attribute='date') | list)[-1] %}
        {{ m.contenu if m.contenu else m.titre }}
      data:
        tag: educartable-message
        clickAction: https://app.educartable.com/messages
        url: https://app.educartable.com/messages
mode: single
```

Home Assistant interroge Educartable toutes les 30 minutes : la notification peut donc arriver avec un petit retard.

## Limites connues

- Connexion par e-mail et mot de passe uniquement (pas de connexion via un fournisseur tiers).
- Les identifiants sont stockés dans la configuration de Home Assistant.
- Les devoirs et messages ne sont pas filtrés par enfant, et le fonctionnement avec plusieurs enfants n'a pas encore été testé.
- L'API d'Educartable n'est pas documentée : elle peut changer sans prévenir et casser l'intégration. Dans ce cas, ouvre une *issue* sur ce dépôt.

## Vie privée

Les capteurs contiennent des informations scolaires concernant des enfants. Ne partage pas de captures d'écran ni de journaux qui montrent ces attributs.

## Soutenir le projet

Cette intégration est gratuite et le restera. Si elle te fait gagner du temps et que tu as envie de dire merci, tu peux m'offrir un café :

<a href="https://ko-fi.com/tillbart"><img alt="Offrez-moi un café" src="https://img.shields.io/badge/☕_Offrez--moi_un_café-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white"></a>

Un retour, une idée ou un bug trouvé m'aident tout autant : n'hésite pas à ouvrir une *issue*.
