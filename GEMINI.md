# Instructions et Règles du Projet

## Mises à jour automatiques et autonomes
- **Mise à jour complète sans confirmation** : Dès qu'un fichier ou bloc de code est modifié, assure-toi systématiquement de tout mettre à jour de bout en bout sans solliciter de confirmation préalable de l'utilisateur.
- **Workflow systématique** :
  1. **Validation** : Vérifier la syntaxe et tester le code (ex: `py_compile`, tests unitaires).
  2. **Métadonnées** : Incrémenter les numéros de version dans les manifests (`manifest.json`) et mettre à jour la documentation (`README.md`, changelog) si applicable.
  3. **Git** : Créer le commit git avec un message conventionnel clair et explicite.
  4. **Push distant** : Exécuter systématiquement le `git push` sur la branche distante (`git push origin main`).
  5. **Déploiement / Synchronisation Home Assistant** : Appliquer ou synchroniser directement les changements vers les cibles requises sans interruption. Pour les intégrations Home Assistant (ex: `ha-strava-gear`, `ha-coros`, `ha-running-races`) :
     - Déclencher le rafraîchissement et l'installation de la mise à jour via l'API / WebSocket HA (`sapsap.fr`).
     - Vérifier la configuration et redémarrer ou recharger Home Assistant si requis.
     - Contrôler l'état des entités pour valider le bon fonctionnement en production.
