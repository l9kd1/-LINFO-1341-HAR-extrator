## [LINFO 1341] HAR data extraction script

### Késako ?
Ce petit script python va vous permettre de générer plein de `.csv` utiles pour l'analyse de site demandée pour le cours de **[LINFO1341] Computer networks**.

Ce serait vachement cool qu'on participe tous à son amélioration.

En bonus voici des petits liens bien utiles:

https://www.tablesgenerator.com/latex_tables

https://roymartinez.dev/2019-06-05-har-analysis/

### Comment m'utiliser ?
Super simple !
1. `git clone https://github.com/l9kd1/-LINFO-1341-HAR-extrator.git`.
2. Tu génères un fichier .har avec ton navigateur préféré et tu le déplaces dans le répertoire où se trouve `analyse.py`.
3. Tu modifies les variables `logname` et `analysed_domains` dans le script `analyse.py` avec les valeurs correctes.
4. `python analyse.py` et le tour est joué !

Si tu as un problème avec le format csv tu peux aller voir le petit script de Amadéo qui pourrait t'aider !

https://github.com/l9kd1/LINFO-1341-HAR-extractor/issues/2

### Requirements
Tu risques de devoir installer le package `pandas`.
