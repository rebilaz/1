# Exemples de prompts pour l’auto-correction

## Prompt type 1 : Correction d’erreur d’exécution

```
Contexte :
Voici le code du worker Python qui a échoué :
---
{code_worker}
---
Voici le log d’erreur obtenu lors de l’exécution :
---
{log_erreur}
---
Corrige le code pour que le worker fonctionne sans erreur. Explique brièvement la correction apportée.
```

## Prompt type 2 : Amélioration de la robustesse

```
Contexte :
Voici le code du worker Python actuel :
---
{code_worker}
---
Rends ce code plus robuste (gestion d’erreurs, logs, docstring, typage, etc.).
```

## Prompt type 3 : Documentation automatique

```
Contexte :
Voici le code du worker Python :
---
{code_worker}
---
Génère une docstring complète et un schéma d’input/output pour ce module.
```
