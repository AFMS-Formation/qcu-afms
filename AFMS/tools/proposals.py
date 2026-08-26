#!/usr/bin/env python3
"""
Propositions de corrections (formateur : à valider).
Format : id -> (lettre_bonne_reponse, difficulté, justification)
Génère app/answers.js en fusionnant avec data/questions.json.

Les lettres A..E correspondent à l'ordre des options dans questions.json.
"""
import json, os, sys

# (lettre, difficulté, justification)
P = {
 # ---- UV02 Juridique ----
 "8fda4a6d08": ("E","facile","Légitime défense (art. 122-5 CP) : riposte à une atteinte injustifiée envers soi ou autrui, nécessaire, proportionnée et simultanée."),
 "49dae8c502": ("A","moyen","Employer un agent sans carte professionnelle est puni de 1 an d'emprisonnement et 15 000 € d'amende (CSI)."),
 "7250fe4def": ("C","moyen","Art. 73 CPP : la personne appréhendée reste sous la surveillance et la protection de celui qui l'a appréhendée jusqu'à sa remise à l'OPJ."),
 # ---- UV03 Gestion des conflits ----
 "2b0ec45f1a": ("E","facile","On désamorce le conflit par des marques de politesse et en justifiant le cadre légal de l'intervention."),
 "c68769da24": ("C","facile","La prévention du conflit passe par une attitude et un comportement exemplaires."),
 "c66eeb1e19": ("C","moyen","Connaître son cadre légal permet de justifier le bien-fondé de son intervention (l'APS a les mêmes prérogatives qu'un citoyen)."),
 "f13733368a": ("D","moyen","Position d'apaisement/protection : mains au niveau du torse, sans agressivité."),
 "322ded9222": ("B","facile","Regarder son interlocuteur sans le fixer trop longtemps (contact visuel non agressif)."),
 "0a99105e78": ("E","moyen","Un avantage auquel on tient et qui est menacé caractérise un conflit d'intérêt."),
 "6736af785a": ("B","facile","Examiner le désaccord et chercher un compromis."),
 "8f28158a27": ("A","facile","Une personne insatisfaite est la plus génératrice de conflit."),
 "0039d2a89f": ("C","moyen","Faire mettre en retrait le personnel de l'organisateur pour résoudre le conflit."),
 "6c174e7187": ("C","facile","Écoute active fondée sur les faits constatés."),
 # ---- UV04 Module stratégique / consignes ----
 "7526f8e74d": ("D","moyen","La consigne d'évacuation affichée près des sorties est une consigne permanente."),
 "4202aadb69": ("D","moyen","Une consigne propre à un local précis (matières toxiques) est une consigne particulière."),
 "050a58caf4": ("B","moyen","Une main courante informatisée peut être consultée à distance par le responsable, au fil des événements."),
 # ---- UV05 Incendie ----
 "39d29ef4c1": ("D","facile","Donner l'alarme puis tenter l'extinction d'un feu naissant."),
 "830cf329d6": ("D","facile","Oui : supprimer un côté du triangle du feu (combustible, comburant, énergie) éteint le feu."),
 "1cabb0aa6c": ("A","facile","IGH = Immeuble de Grande Hauteur."),
 "7a551ad4b0": ("D","facile","L'extincteur CO2 se reconnaît à son tromblon (diffuseur)."),
 "1ef70ababd": ("E","facile","Le comburant est un côté du triangle du feu (avec le combustible et l'énergie d'activation)."),
 "a9e342358e": ("A","moyen","Distance d'attaque d'un extincteur à eau : environ 2 à 3 mètres. (à confirmer)"),
 # ---- UV06 Appréhension art. 73 ----
 "79e5a8606a": ("B","facile","Après appréhension, aviser sans délai les forces de l'ordre."),
 "c570eaf77e": ("E","moyen","La flagrance inclut la personne poursuivie par la clameur publique (art. 53/73 CPP)."),
 "9339abcd66": ("C","moyen","La dégradation volontaire est un délit flagrant puni d'emprisonnement : appréhension possible."),
 "e935e00b22": ("B","moyen","Une caméra de vidéosurveillance est fortement recommandée dans un local d'appréhension."),
 "22a339bd6a": ("E","facile","Art. 73 CPP : tout citoyen peut appréhender l'auteur d'un crime/délit flagrant puni d'emprisonnement."),
 "25b0651ab6": ("C","facile","L'agent agit normalement ; il est conseillé d'appeler un témoin féminin."),
 # ---- UV07 Sûreté / terrorisme / secours ----
 "82e5a90989": ("D","moyen","Se jeter au sol, à plat ventre, face contre terre. (à confirmer)"),
 "eb3eeff893": ("C","moyen","Les palpations dans un périmètre de protection sont décidées par le préfet via un arrêté."),
 "8c501aa410": ("E","moyen","Oui, la loi autorise l'entrave d'un individu appréhendé sous certaines conditions."),
 "420aff088a": ("E","facile","NRBC-E = Nucléaire, Radiologique, Biologique, Chimique et Explosif."),
 "7f1adf3d8e": ("E","facile","Plaie par balle sur un membre qui saigne abondamment : poser un garrot dès que possible."),
 "a3d952c7a3": ("D","facile","L'attentat suicide utilise généralement un engin explosif."),
 "0e0857b191": ("A","facile","Doctrine : Courir / se Cacher / Combattre en dernier recours."),
 "0ee6ed86be": ("A","difficile","Alerter les secours immédiatement par tous moyens. (à confirmer : la doctrine « réagir » privilégie l'alerte une fois à l'abri)"),
 "67a49628b9": ("D","facile","Un attentat à l'aveugle ne vise personne en particulier."),
 "cc22eca5a6": ("E","facile","Hémorragie artérielle : le sang s'écoule abondamment, par saccades."),
 # ---- UV08 Surveillance & rondes ----
 "0fca091993": ("B","facile","Le plan Vigipirate vise à prévenir la menace terroriste."),
 "4455e9855d": ("C","moyen","Le vol commis par plusieurs personnes (en réunion) est une circonstance aggravante."),
 "35725b3bc7": ("D","facile","Alphabet international : P=Papa, C=Charlie, S=Sierra."),
 "54a8bc30d1": ("E","facile","Oui, une bonne présentation est nécessaire durant le service."),
 "df0710c8ed": ("E","facile","Dans un premier temps, se présenter avec courtoisie."),
 "6d287eb99c": ("E","difficile","Oui : les convoyeurs en véhicule banalisé peuvent être dispensés du port de la tenue. (à confirmer)"),
 "f4c02950ac": ("C","moyen","Non : en véhicule banalisé, les convoyeurs de fonds ne sont pas armés (l'armement concerne le fourgon blindé)."),
 "13c3e5dd01": ("B","moyen","Familles de détecteurs : optiques, thermiques, de mouvements, microphoniques."),
 "39abe89d30": ("A","facile","Les moyens de liaison (radio, téléphone) sont les moyens de communication de l'agent."),
 "13a87161f1": ("A","moyen","L'APS peut sécuriser les locaux pendant une grève (sans entraver le droit de grève)."),
 "1a0bb92fae": ("A","moyen","Point vulnérable : point dont l'atteinte handicaperait le bon fonctionnement de l'entreprise."),
 "8b820f1227": ("D","moyen","La protection périphérique concerne la limite extérieure (clôture)."),
 "f4e0b3c8eb": ("D","moyen","La protection volumétrique concerne le volume d'un local."),
 "71bd0de400": ("B","moyen","L'agent au PC dépêche le rondier sur le lieu de l'alarme pour la levée de doute et reste au PC."),
 "649cf9ea8b": ("C","facile","J-O-H-N : Juliet, Hôtel, Oscar, November."),
 # ---- UV09 Palpation / événementiel ----
 "6f28b18e21": ("C","moyen","Périmètre de protection : agent désigné, palpation d'une personne de même sexe avec son accord, sous la responsabilité d'un OPJ."),
 "7ced7baac5": ("E","moyen","Les membres du service d'ordre effectuant des palpations doivent porter un signe distinctif identifiant leur qualité."),
 "f0d93e2970": ("B","difficile","« Sous le contrôle d'un OPJ » : un OPJ désigné par le préfet, en situation d'astreinte (présence physique non exigée). (à confirmer)"),
 "3c04bd64ac": ("B","moyen","Palpation possible dans le cadre de l'état de nécessité (art. 122-7 CP)."),
 "ba7c7dbaba": ("B","moyen","Manifestations sportives : agents habilités par l'employeur puis agréés par le préfet de département."),
 "0ae9d0b040": ("D","moyen","Aucune des propositions : la palpation se fait au-dessus des vêtements, sans fouille ni magnétomètre."),
 "057655375b": ("E","moyen","Obligation de palpation pour l'accès aux manifestations de plus de 300 spectateurs (CSI)."),
 "5f41b6cbb7": ("C","moyen","Par mesure de sécurité, l'arme peut être saisie d'autorité."),
 "ce49deb82e": ("E","moyen","Par mesure de sécurité, l'arme peut être saisie d'autorité."),
 "9b20d6a033": ("A","moyen","Palpation à l'entrée d'un magasin : seulement si un arrêté préfectoral le prescrit ou en état de nécessité."),
 "cb03b6af84": ("D","moyen","Sans agrément préfectoral, l'agent informe l'employeur qu'il n'a pas le droit d'effectuer la palpation."),
 # ---- UV10 ----
 "78728853e1": ("D","moyen","Plan de prévention obligatoire dès que la durée des travaux atteint 400 heures sur 12 mois (ou travaux dangereux)."),
 "110e7786eb": ("B","difficile","Refus : sans agrément/arrêté et sous le seuil de 300 personnes, la palpation n'est pas autorisée. (à confirmer)"),
 "7fe314f51c": ("B","moyen","Refus : la vidéoprotection a une finalité de sûreté, pas le contrôle des extincteurs (détournement de finalité)."),
 # ---- UV11 ----
 "c158a34ab7": ("E","moyen","En cas de défaillance du DATI, l'agent effectue des appels sécuritaires selon les consignes de site."),
 "77aa1c4d96": ("A","facile","Fournir aux secours les plans de l'établissement."),
 "9aed309063": ("B","moyen","Le DATI/PTI déclenche notamment une alarme de perte de verticalité (homme à terre)."),
 "eabb5eafb5": ("D","difficile","La découverte d'une victime (secours à personne) est prioritaire. (à confirmer)"),
 "2df12b709b": ("B","difficile","Effets du courant électrique : troubles cardiovasculaires notamment. (à confirmer)"),
 "2196dba9c6": ("A","moyen","Défaut technique : appeler l'électricien de l'établissement conformément aux consignes."),
 "5ecf3e0039": ("B","moyen","Fuir si possible sinon se confiner, et contacter le 114 (numéro d'urgence par SMS)."),
 "6ead1d7dfd": ("B","facile","Envoyer un membre du personnel ouvrir l'accès aux services de secours."),
 "a2d4c9fa25": ("C","moyen","DAI = alarme feu ; TGBT = local « Tableau Général Basse Tension »."),
 # ---- UV12 ----
 "e31776a485": ("D","difficile","PPI : prévoir la mobilisation des services de secours publics autour des installations classées. (à confirmer)"),
 "c74f903c69": ("A","facile","Le contrôle d'accès électronique autorise l'accès à des personnes déterminées."),
 "5965c004bb": ("E","moyen","Accès frauduleux aux données : atteinte aux systèmes de traitement automatisé de données (STAD)."),
 "baa7618fdf": ("D","moyen","Le schéma d'installation permet de capter, transmettre, stocker et visionner les images."),
 "231a0aa6cb": ("D","moyen","Un dépôt de matières incombustibles n'est pas classé SEVESO/à risque."),
 "abd7a17221": ("A","facile","Un risque se caractérise par sa gravité et sa probabilité d'occurrence (fréquence)."),
 "2d17bec57e": ("C","moyen","Plan de prévention impératif pour les travaux dangereux listés à l'arrêté du 19 mars 1993."),
 "469e9895b3": ("C","moyen","Plan ORSEC : appliquer les consignes et plans d'intervention prévus."),
 "5d73c5329b": ("E","facile","La CNIL protège la vie privée et les libertés publiques."),
 "37a68485af": ("C","moyen","Autorisé : conserver les images un mois au maximum, sauf procédure judiciaire en cours."),
 "8dbf5fe307": ("C","moyen","Oui, accès de droit, sauf refus justifié par les conditions fixées par la loi."),
 "892ce0ee6b": ("A","moyen","Oui, l'accès aux enregistrements est de droit, sous certaines conditions."),
 "9d16caf8ac": ("C","moyen","Refus : la vidéoprotection n'est pas destinée au contrôle des extincteurs (détournement de finalité)."),
 "4693edf2de": ("A","facile","À la prise de service, vérifier le bon fonctionnement des caméras conformément aux consignes."),
}

# ---- LOT 2 : UV02, UV04, UV10, UV11, UV12, UV14 ----
P.update({
 # UV02
 "a5116f393a": ("D","","Perte du permis : prévenir l'employeur pour mettre en place une solution transitoire (on ne conduit plus)."),
 "9b226fc1da": ("A","","Victime de violences : se faire examiner par un médecin (arrêt de travail) ; un dépôt de plainte reste possible."),
 "eb2357b5ec": ("D","","Le Livre VI impose à l'employeur de s'assurer de l'adéquation des qualifications de ses employés avec les missions."),
 "1d82dbe147": ("C","","La confidentialité s'impose sous réserve des cas prévus ou autorisés par la loi (ex. procédure judiciaire)."),
 "8592b3158f": ("A","","Renouvellement régulier : l'agent peut travailler avec le récépissé du CNAPS (art. R612-17 CSI)."),
 "70d0788cae": ("B","","PLS : victime inconsciente qui respire."),
 "665d8d99b8": ("D","","La carte professionnelle est personnelle à l'agent : il la conserve en fin de contrat."),
 "a0d35f423a": ("D","","On ne peut, sans motif légitime, refuser d'exécuter une réquisition légale, sous peine de poursuites."),
 "babef3fcbc": ("A","","Demande de renouvellement à présenter au moins 3 mois avant l'expiration. (à confirmer)"),
 "ffe0d2145e": ("C","","La formation continue (MAC) est à la charge de l'employeur."),
 "b8583f63db": ("C","","Le renouvellement de la carte pro est subordonné au suivi d'une formation continue (MAC)."),
 "72b4078af1": ("D","","La condition de recrutement est garantie par la carte professionnelle valide dématérialisée délivrée par le CNAPS."),
 "ffe919f0fd": ("C","","Pour accéder à la formation, le candidat doit obtenir une autorisation préalable (ou provisoire) d'exercice."),
 "1e9d29da26": ("B","","La légitime défense suppose une attaque actuelle/récente (imminente)."),
 "a21c2e4389": ("A","","Le CNAPS consulte le bulletin n°2 du casier judiciaire."),
 "5a488106de": ("A","","Non applicable : l'interdiction temporaire d'exercer est de 5 ans maximum, pas 7 ans."),
 "d086bb0bed": ("A","","Éléments constitutifs de l'infraction : légal, matériel, moral."),
 "5331a6a12c": ("C","","Les EPI sont fournis par l'employeur."),
 "013c11c405": ("D","","L'employeur doit s'assurer de l'adéquation des qualifications de ses employés avec les missions confiées."),
 # UV04
 "c7ac328e4e": ("D","","Sur la main courante on consigne les faits liés à la sécurité, dont les alarmes techniques."),
 "6cb96b711a": ("D","","La main courante n'est pas imposée par la loi, mais protège en cas de saisie par les autorités. (à confirmer)"),
 "d8cdaaca3d": ("D","","Le compte rendu écrit sert à signaler un fait circonstancié, urgent et important."),
 "491b1f0e87": ("A","","On respecte les consignes d'hygiène du site client (charlotte, blouse, sur-chaussures)."),
 "0a5436a7be": ("C","","Le numéro de version permet de savoir si la consigne en vigueur est la bonne."),
 "bbeda5b866": ("A","","On transmet les consignes via l'émetteur-récepteur portatif (radio)."),
 "fcf9977a13": ("B","","Chaîne de télésécurité : Détection – Transmission – Réception – Traitement – Intervention."),
 "d939869737": ("B","","On s'authentifie (mot de passe) auprès du télésurveilleur et on se rend sur place pour la levée de doute."),
 "3babbe21de": ("C","","Une consigne ponctuelle peut être orale mais doit être reportée à l'écrit."),
 "ea338c101e": ("D","","Procédure simplifiée possible si les marchandises sont restituées ou payées (et les faits reconnus)."),
 "a788c82d79": ("E","","La protection ponctuelle concerne un objet précis."),
 "1faa9f0f3d": ("A","","On conserve une main courante papier en secours si l'informatisée tombe en panne."),
 "d1e8e2a4b0": ("E","","On regarde le client et on le salue (« bonjour »)."),
 "f483d9d645": ("C","","En attendant, on consulte les consignes intrusion pour ne rien oublier."),
 # UV10
 "0bc4644a86": ("B","","On informe immédiatement le responsable sécurité selon les consignes (pas d'action directe)."),
 "281d6d24e9": ("E","","CNIL = Commission Nationale de l'Informatique et des Libertés."),
 "79c99fd8ec": ("C","","Sans caméra, être accompagné d'un autre APS ou d'un collaborateur client (témoin)."),
 "a918ba0da1": ("E","","Le DATI se justifie pour un travailleur seul/isolé sur un site."),
 "f3400b4b45": ("C","","La caméra fait partie d'un système de vidéosurveillance."),
 "44193b12c9": ("B","","Différence caméra IP / analogique : la façon dont le signal est transmis."),
 "d597e828ea": ("B","","Différence caméra IP / analogique : la façon dont le signal est transmis."),
 "fe8d7f592d": ("A","","Aggravation : s'être laissé enfermer volontairement (introduction par ruse). (à confirmer)"),
 "3806bd7158": ("C","","Accès de droit aux enregistrements, sauf refus justifié par les conditions fixées par la loi."),
 "4ea6eaa2cb": ("E","","Accès de droit aux enregistrements, sauf refus justifié par les conditions fixées par la loi."),
 "1a8b966d09": ("C","","Oui, l'accès aux enregistrements est de droit, sous certaines conditions."),
 "42b2e46e76": ("E","","Refus : supprimer des images exposerait à des poursuites pénales et disciplinaires."),
 "6adfa3f16c": ("C","","Aux forces de l'ordre : présentation, adresse, numéro de téléphone, nature de l'incident."),
 # UV11
 "0045f6d0e4": ("D","","Défaillance DATI : faire des appels sécuritaires selon les consignes du site."),
 "e5fa787176": ("D","","Port/transport d'armes de catégorie D sans agrément : délit, 1 an d'emprisonnement et 15 000 € d'amende."),
 "7e09561536": ("D","","Port/transport d'armes de catégorie D sans agrément : délit, 1 an d'emprisonnement et 15 000 € d'amende."),
 "d3a78ee738": ("E","","On analyse d'abord la réaction des personnes de l'endroit d'où il sort avant toute action."),
 "cb69b88123": ("B","","On analyse d'abord la réaction des personnes de l'endroit d'où il sort avant toute action."),
 "964aa49248": ("D","","Le courant électrique provoque notamment la tétanisation des muscles."),
 "6487b92f59": ("C","","La GTB gère le fonctionnement des installations techniques du bâtiment. (à confirmer)"),
 "36d48b1368": ("E","","Le DATI se déclenche notamment en cas d'arrachement et/ou d'agression physique."),
 "c5c2ef9860": ("C","","Le DATI se déclenche notamment en cas d'arrachement et/ou d'agression physique."),
 "bbf776fe17": ("A","","Alarmes du DATI : déclenchement volontaire et perte de verticalité."),
 "739b461809": ("E","","Alarme surchauffe chaufferie : appeler le technicien compétent selon les consignes. (à confirmer)"),
 "c8a2feb137": ("A","","Arrachage de sac : vol en flagrant délit, appréhension possible."),
 "59aa4427d0": ("B","","Le DATI est un maillon de la chaîne de sécurité : il émet un signal déclenchant une procédure prédéfinie."),
 # UV12
 "d8f80b8536": ("C","","On écoute le client et on le dirige vers le service chargé des litiges."),
 "8aba0b5532": ("D","","Avant la manifestation : procéder à l'inspection des installations ou de la salle."),
 "b7219910ad": ("B","","Avant la manifestation : procéder à l'inspection des installations ou de la salle."),
 "b9b683a35b": ("D","","Les événements quotidiens s'écrivent en noir (le rouge est réservé aux incidents)."),
 "47e7115a06": ("C","","Déclaration aux maires ou préfets de police pour une manifestation pouvant atteindre plus de 1 500 personnes (R211-22). (à confirmer)"),
 "0ae4452828": ("C","","Facteur aggravant : billets vendus au dernier moment, sans places réservées."),
 "46726d97b2": ("A","","Question dégradée dans la source (options tronquées). (à confirmer)"),
 "f039aadc64": ("D","","On écoute, on argumente et on propose des solutions conformément aux consignes."),
 "48ee344cc6": ("E","","Une visite VIP annoncée pour le lendemain est une consigne ponctuelle."),
 "be15cba8df": ("E","","La main courante relate tous les événements/incidents liés à la sécurité de la vacation."),
 "66892ec07d": ("C","","Événement grave : compte rendu oral immédiat par téléphone, puis transmission écrite par email."),
 "f92bf2fb64": ("A","","On écoute le client et on le dirige vers le service chargé des litiges."),
 # UV14
 "befe981781": ("B","","Le plan de prévention est rédigé avant la prestation (les travaux)."),
 "66d35d086b": ("A","","Les mesures des secours extérieurs figurent dans le Plan Particulier d'Intervention (PPI) ou équivalent."),
 "159677be4d": ("A","","Les mesures des secours extérieurs figurent dans le Plan Particulier d'Intervention (PPI) ou équivalent."),
 "53e31b7c5e": ("E","","Le plan ORSEC organise la réponse de la sécurité civile."),
 "a0adce327a": ("C","","ICPE = Installation Classée pour la Protection de l'Environnement."),
 "d63438e8f4": ("E","","Plan de prévention obligatoire dès que la durée des travaux atteint 400 h sur 12 mois (ou travaux dangereux)."),
 "b54de5c8f8": ("B","","Sur un site SEVESO s'applique le Plan d'Opération Interne (POI) ou équivalent."),
 "6609d71aa8": ("E","","Document SEVESO concernant l'APS : le Plan d'Opération Interne (POI) ou équivalent."),
 "ad9de69c74": ("C","","Document SEVESO concernant l'APS : le Plan d'Opération Interne (POI) ou équivalent."),
 "44a6ca1657": ("B","","Concernés au premier chef : l'entreprise utilisatrice et l'entreprise extérieure."),
 "4cd959e956": ("D","","Concernés en priorité : l'entreprise utilisatrice et l'entreprise extérieure."),
 "f993204308": ("E","","Consigne pour accéder à un local de matières toxiques : consigne particulière."),
})

# ---- LOT 3 : UV03, UV05, UV06, UV07 ----
P.update({
 # UV03
 "8125109a33": ("C","","Rébellion : résistance violente à un représentant des forces de l'ordre agissant dans l'exercice de ses fonctions."),
 "37c47fbc7f": ("B","","Pointer quelqu'un du doigt : attitude menaçante ou arrogante."),
 "e0747c132e": ("C","","Il est interdit à la sécurité privée de s'immiscer dans un conflit du travail."),
 "00350a931c": ("D","","Légitime défense : droit de se défendre ou de défendre autrui contre une atteinte injustifiée."),
 "00c7dd317f": ("B","","Le compte rendu est un moyen de communication simple et direct avec sa hiérarchie."),
 "e4fb024cae": ("C","","Bras croisés : attitude fermée."),
 "7848a4372b": ("A","","Un conflit non clairement déclaré est latent."),
 "46c8b737ea": ("D","","Face à un conflit dans son périmètre, l'agent se pose en médiateur."),
 "a4aa25eec5": ("B","","La bienveillance n'est pas un facteur déclenchant de l'agressivité."),
 "384983c474": ("C","","Un conflit : opposition entre personnes n'ayant pas trouvé de solution."),
 "eddee63e83": ("E","","À éviter en conflit : mettre en garde et imposer une solution."),
 "5069077163": ("B","","Rôle de l'APS : sécurisation des biens et des personnes."),
 "4af5fcef85": ("E","","Résoudre un conflit : Écouter - Reformuler - Interroger - Confirmer."),
 "76620c5f35": ("D","","On écoute, on argumente et on propose des solutions conformément aux consignes."),
 "d4471ecce4": ("D","","Première attitude pour résoudre un conflit : le dialogue constructif."),
 "51e90be6c2": ("C","","Être exposé à des préjugés peut générer un conflit."),
 "841debe4f3": ("C","","Rester calme, gérer le problème et, en cas d'échec, informer sa hiérarchie."),
 "6e5a2d55ed": ("A","","Défense légitime : nécessaire, dans le même temps, proportionnée à la gravité de l'atteinte."),
 "d17330fa75": ("D","","Gérer un conflit : Écoute active – Affirmation de soi – Recherche d'un compromis."),
 "e76b185a9e": ("D","","Rester ferme et diplomate, proposer de contacter directement son responsable."),
 "dd8333b3e0": ("A","","Une opposition d'idées avec hostilité pour atteindre son objectif = un conflit."),
 "47e28c43db": ("D","","Ne rien faire : omission d'empêcher un crime ou un délit contre l'intégrité d'une personne."),
 "383f9bdd06": ("B","","On épelle grâce à l'alphabet international."),
 # UV05
 "3a448c8b6a": ("B","","Deux types de pression : permanente et auxiliaire."),
 "ef6b2fce16": ("B","","Cinq classes de feu : A, B, C, D, F."),
 "f8f2117014": ("E","","La tenue ne doit entraîner aucune confusion avec celle des agents des services publics."),
 "f901cdf64c": ("C","","Eau pulvérisée : feux de classe A (ex. feu de poubelles)."),
 "e12e80b05b": ("E","","Eau pulvérisée : feux de classe A (ex. feu de poubelles)."),
 "458a53b43e": ("C","","Interventions incendie notées en rouge sur la main courante."),
 "b359ec3a2e": ("E","","Interventions incendie notées en rouge sur la main courante."),
 "f9d270a98f": ("B","","L'alarme restreinte est reçue sur l'ECS (Équipement de Contrôle et de Signalisation)."),
 "8dc71df48a": ("B","","Acquittement du signal, lecture de l'information, levée de doute, plan d'action conforme aux consignes."),
 "d4f1b19466": ("C","","On priorise la détection incendie, dont la gravité peut être supérieure."),
 "4c88e7e7bd": ("B","","On priorise la détection incendie (plus grave)."),
 "354412cd0a": ("B","","Ronde de fermeture : contrôler la fermeture des fenêtres."),
 "1f59a052d1": ("C","","Classe F : feux de graisses/huiles servant d'auxiliaires de cuisson."),
 "5615cd6782": ("E","","Pas d'obligation spécifique de DATI, mais l'employeur doit garantir qu'aucun travailleur isolé ne reste sans secours à bref délai."),
 "56b0eaaf75": ("E","","Le feu d'origine électrique n'est pas une classe de feu (l'électricité est une cause) : aucune des classes."),
 "093d827834": ("E","","Priorité des acteurs de la sécurité privée : aider la justice et les services de police."),
 "4ae42e6afa": ("C","","L'extincteur CO2 se reconnaît à son tromblon."),
 "c72b8a8921": ("D","","R.I.A = Robinet d'Incendie Armé."),
 "7c716494fa": ("A","","Combustion : combustible, comburant, énergie d'activation (triangle du feu)."),
 "7d9f88042a": ("E","","On confirme la levée de doute en identifiant si possible le voyant rouge allumé sur le détecteur."),
 "f89b84ad8f": ("E","","L'extincteur CO2 est à pression permanente, pas auxiliaire : non."),
 "aa6244e86b": ("D","","L'extincteur CO2 est à pression permanente : oui."),
 "c133191890": ("D","","L'extincteur CO2 est à pression permanente, pas auxiliaire : non."),
 "45e48fcb28": ("D","","Voyant rouge fixe sur l'ECS du SDI : une alarme feu."),
 "49f9062e1b": ("C","","Une arme à répétition automatique est de catégorie A (A2). (à confirmer)"),
 "4e79b0e5ae": ("A","","Délit flagrant : le délit se commet actuellement."),
 "cc27af71f3": ("A","","Travaux par points chauds sans permis-feu : contacter le PCS et, selon consigne, faire cesser les travaux."),
 "4630dc7d85": ("E","","Feu d'armoire électrique : couper l'électricité au préalable."),
 "70faa04562": ("E","","Après l'alerte : envoyer un membre du personnel réceptionner les secours."),
 "b8dc955600": ("C","","On privilégie la levée de doute de l'alarme incendie."),
 # UV06
 "4abf14e44f": ("C","","Le droit d'appréhender découle de l'article 73 CPP (non listé) : aucune des autres réponses. (à confirmer)"),
 "d98648ac8b": ("A","","Précaution : être accompagné(e) d'un agent en renfort."),
 "a390784c23": ("A","","Le droit d'appréhender découle de l'article 73 CPP (non listé) : aucune des autres réponses. (à confirmer)"),
 "ec9465c3bf": ("A","","La personne appréhendée reste sous la responsabilité de l'agent qui l'a appréhendée."),
 "49cc500a96": ("B","","L'article 73 CPP est un droit de tout citoyen."),
 "81cf27f51f": ("C","","L'article 73 CPP est un droit de tout citoyen."),
 "f146e39487": ("D","","Précaution dans le local d'interpellation : être accompagné d'une tierce personne (témoin)."),
 "ea9a7ca3b6": ("A","","Donner l'alerte et établir un périmètre de sécurité pour préserver les traces."),
 "7c76bed450": ("E","","Le droit d'appréhender est encadré par l'article 73 du Code de procédure pénale."),
 "2c4f0febcc": ("D","","Le droit d'appréhender est encadré par l'article 73 du Code de procédure pénale."),
 "a6dbf12153": ("C","","On peut appréhender en surface de vente en cas de flagrant délit. (à confirmer)"),
 "60241888df": ("D","","Consommer un produit sans le payer est un vol (délit) : appréhension possible."),
 "0043630a31": ("B","","Vol commis la semaine passée : pas de flagrance, pas d'appréhension."),
 "50f79a2f69": ("E","","Vol commis la semaine passée : pas de flagrance, pas d'appréhension."),
 "56306c5eeb": ("E","","Dégradation volontaire : délit flagrant, appréhension possible."),
 "3c3ac6ccc6": ("A","","Vol d'un CD en surface de vente : flagrant délit, la loi autorise l'appréhension."),
 "82ae4be5b6": ("C","","Le chef d'équipe réunit les agents concernés pour résoudre le problème."),
 "40a58af131": ("B","","Article 73 CPP : n'importe quel citoyen peut appréhender l'auteur d'un délit flagrant puni d'emprisonnement."),
 "75da0386ee": ("A","","Chaufferie gaz : entrée possible avec un matériel anti-déflagrant (ATEX)."),
 "13dafa5ddd": ("A","","Il agit normalement ; il est conseillé d'appeler un témoin féminin."),
 "a4ff1620e7": ("D","","Quel que soit le sexe, il agit conformément à l'article 73 du CPP."),
 "05acfd63b2": ("D","","Flagrant délit : on applique l'article 73 du CPP, sans favoritisme. (à confirmer)"),
 "049f69faf7": ("A","","Flagrance : possession d'objets du magasin hors surface de vente, sans justificatif d'achat."),
 "dfad4a8d15": ("D","","Agression pendant l'appréhension : réagir en respectant les conditions de la légitime défense."),
 "4c7cdb339d": ("C","","Obligation : faire prévenir un officier de police judiciaire (OPJ)."),
 "e0e46817cc": ("B","","Obligation : faire prévenir un officier de police judiciaire (OPJ)."),
 "e0906b8706": ("B","","On peut utiliser la force strictement nécessaire au but recherché."),
 "fe914f30cb": ("C","","Aviser le PC pour organiser l'appréhension en cas de sortie sans achat (vol consommé à la sortie)."),
 # UV07
 "6bc3c1666a": ("D","","Grands événements exposés : désignés par décret (art. L211-11-1 CSI)."),
 "ebebcda848": ("D","","« Terrorisme » vient de « terreur »."),
 "505a668e5c": ("B","","On ne déclenche pas l'alarme incendie : cela provoquerait un regroupement de personnes."),
 "48e7cd4e6c": ("B","","Durant un attentat, on ne revient pas sur la zone attaquée, dans tous les cas."),
 "a0d3e20a73": ("D","","À l'arrivée des forces de l'ordre : suivre leurs instructions."),
 "362533feb6": ("D","","L'obligation de discrétion s'exerce de façon permanente."),
 "4ff11b5357": ("E","","La première équipe intervient pour neutraliser les tireurs actifs."),
 "684cd8877c": ("D","","Le vol avec arme est un crime."),
 "36c998556c": ("E","","Armement possible d'un bâton de défense de type TONFA (catégorie D, sous conditions). (à confirmer)"),
 "4b40578091": ("C","","Mode opératoire terroriste traditionnel : prise d'otage et exécution."),
 "8d2f07f59f": ("C","","Traumatisme post-attentat : consulter un médecin spécialisé."),
 "0f63275a7d": ("C","","Traumatisme post-attentat : consulter un médecin spécialisé."),
 "18e4230cef": ("C","","Terrorisme d'État : un État qui terrorise son peuple."),
 "d22709b41d": ("D","","On observe le comportement (pas la religion ni l'apparence)."),
 "db14ed126d": ("B","","RETEX = Retour d'Expérience."),
 "73a859d428": ("D","","Le « R » de NRBC-E = Radiologique."),
 "e5768ed087": ("E","","Objectif du plan Vigipirate : développer et maintenir la vigilance."),
 "350562fd89": ("B","","Les deux documents clés : consignes générales et consignes particulières."),
 "da28777474": ("D","","On sort avec les mains visibles."),
 "3fc747e0cf": ("C","","Plaie soufflante au torse : pansement 3 côtés pour éviter le pneumothorax."),
 "daca77f798": ("B","","Soupçon de radicalisation : contacter le numéro vert (0 800 00 56 96) ou le formulaire en ligne."),
 "c2750ecfc8": ("C","","Inspection visuelle possible, par exemple si un portique antivol se déclenche. (à confirmer)"),
})

# ---- LOT 4 : UV08, UV09 ----
P.update({
 # UV08
 "f8bbd0ca5e": ("E","","Losange blanc à bord rouge avec flamme : produit inflammable."),
 "fb0d62a3f6": ("C","","Crash barrière : barrières de sécurité lestées/à pieds empêchant le renversement. (à confirmer)"),
 "c729e3cb1a": ("E","","Ne fait pas partie des missions : rassembler les groupes antagonistes (dangereux)."),
 "fbf82379f8": ("E","","Trois zones de protection : périphérique, volumétrique, ponctuelle. (à confirmer)"),
 "d6c736145d": ("D","","Dispense de tenue : surveillance contre le vol à l'étalage (agent en civil)."),
 "9226cd4cee": ("A","","RCP : défibrillateur automatisé externe (DAE)."),
 "f6fbe94359": ("C","","Un point sensible est un point convoité (par les malveillants/voleurs)."),
 "71784fd884": ("B","","Ne fait pas partie des missions : rassembler les groupes antagonistes."),
 "9bf3556dbd": ("D","","Devoir de réserve : ne pas divulguer les informations relatives au fonctionnement de l'entreprise."),
 "d133d7f886": ("B","","Demander à l'interlocuteur de rappeler ultérieurement (ne pas communiquer le GSM)."),
 "c74cfcce0d": ("D","","L'agent porte la tenue de son entreprise (son employeur). (à confirmer)"),
 "b583b2ff50": ("B","","L'air contient environ 21 % d'oxygène."),
 "2633a51760": ("D","","L'air contient environ 21 % d'oxygène."),
 "31b58d32f7": ("C","","L'évaluation des risques professionnels figure dans le document unique."),
 "ce1fa407c8": ("A","","L'évaluation des risques professionnels figure dans le document unique."),
 "e8868bf5be": ("B","","La convention collective est tenue à la disposition des salariés dans l'entreprise."),
 "25a0bb38d7": ("A","","Le report d'alarme permet d'accéder à certaines informations hors du PCS. (à confirmer)"),
 "1c8032adc7": ("E","","L'APS se comporte dignement en toutes circonstances."),
 "1d3d5f16a8": ("E","","Oui : les convoyeurs en véhicule banalisé peuvent être dispensés du port de la tenue. (à confirmer)"),
 "80aaa66295": ("B","","Document confidentiel trouvé : demander au PCS de prévenir un responsable du site."),
 "a16dbaaacb": ("B","","Parler poliment, rester calme et exprimer son point de vue."),
 "4d2a5b7243": ("C","","Le signaler à l'arrière-caisse et poursuivre la surveillance de la zone de vente."),
 "083ee5416b": ("E","","Le signaler à l'arrière-caisse et poursuivre la surveillance de la zone de vente."),
 "b73daa7b02": ("C","","Aucun travailleur ne doit rester isolé en un point où il ne pourrait être secouru à bref délai."),
 "3d1a14f826": ("B","","Aucun travailleur ne doit rester isolé en un point où il ne pourrait être secouru à bref délai."),
 "c80eaed46b": ("A","","Prévenir immédiatement le PCS et inspecter prudemment les locaux voisins."),
 "e4015e9216": ("D","","Aucune des propositions n'est proportionnée (évacuer selon consignes, OPJ si résistance). (à confirmer)"),
 "fe416ae569": ("E","","ERP = Établissement Recevant du Public."),
 "85e1739a14": ("A","","Tireur actif : tue de manière aléatoire."),
 "ed8df17d24": ("A","","État d'urgence : régime exceptionnel permettant à l'État de gérer une crise."),
 "969ed9f1f0": ("C","","Zone d'exclusion : zone de danger et d'intervention."),
 "e11ec76c7c": ("B","","On alerte les forces de l'ordre dès que l'intrusion est confirmée (après levée de doute)."),
 "3e3bf1daed": ("C","","En arrivant sur site, l'APS se met en tenue."),
 "737315dd90": ("A","","TFP APS = Titre à Finalité Professionnelle Agent de Prévention et de Sécurité."),
 "8cba9e3efe": ("D","","TFP APS = Agent de Prévention et de Sécurité (option scindée dans la source). (à confirmer)"),
 "f92d3430b5": ("D","","Clôturer un site rend l'évacuation plus difficile."),
 "297e039481": ("C","","But de la protection mécanique : freiner la progression d'un intrus."),
 "3addd3627b": ("E","","L'ECS collecte les informations des DAI et des déclencheurs manuels (DM)."),
 "f94f4d78d1": ("D","","Protéger d'abord les lieux puis prendre en charge la victime."),
 "a0f5df2c3b": ("D","","Le dépôt de plainte relève du responsable du magasin habilité, pas du chef de poste."),
 "5ac3c416d0": ("E","","DAI sollicité : alarme restreinte au PCS."),
 "c2d8068872": ("B","","DAI sollicité : alarme restreinte au PCS."),
 "065ba67fb4": ("A","","Lui demander où il se trouve, de s'asseoir/s'étendre, en attendant les secours."),
 "8ae7e5d103": ("D","","Le rapport circonstancié indique l'ensemble des informations de l'incident."),
 "17cb5b920c": ("C","","Un revolver .38 Special (arme de poing) est de catégorie B."),
 "283dea2608": ("A","","Secours à personne (urgent) : s'excuser et repartir rapidement en intervention."),
 "92cc70ad6d": ("A","","Envoyer un membre du personnel ouvrir l'accès aux secours."),
 "710d44ecce": ("D","","On prévient ses collègues pour une appréhension en sortie sans achat (pas de favoritisme)."),
 "28851eb3a4": ("D","","Le chef de poste organise une réunion de conciliation."),
 "8d1ba2f20e": ("E","","L'alarme générale sélective prévient une catégorie de personnel."),
 # UV09
 "01df7fa594": ("C","","En filtrage : recueil d'identité possible si les consignes/le règlement intérieur le prévoient."),
 "7fb78c4319": ("C","","Mineur voleur : on appelle les forces de l'ordre (pas de fouille ni reconnaissance)."),
 "e0ea5a058d": ("A","","Risque d'attentat : le préfet peut interdire la circulation, instaurer un couvre-feu, limiter les allées et venues."),
 "1bc74e911b": ("C","","Appréhension si l'individu commet un délit ou un crime sur le site."),
 "3fba787c24": ("A","","Palpation possible sur une personne appréhendée en flagrant délit menaçant sa propre intégrité (état de nécessité)."),
 "43b0d0dd97": ("B","","Palpation possible dans tout lieu visé par un arrêté préfectoral."),
 "cb2eaac86b": ("D","","La palpation, c'est passer les mains par-dessus les vêtements pour vérifier l'absence d'objets dangereux."),
 "8db504b81f": ("D","","Événement de plus de 300 personnes : agrément de palpation délivré par le préfet."),
 "b0260aab22": ("E","","Oui, on peut palper une personne en situation de handicap, en respectant certaines règles."),
 "d25290101d": ("E","","Après une appréhension en flagrant délit, palpation possible en cas d'état de nécessité."),
 "6de2e1c988": ("B","","Inspection visuelle des bagages et, avec le consentement du propriétaire, fouille."),
 "004cd51031": ("E","","Inspection visuelle des bagages et, avec le consentement du propriétaire, fouille."),
 "f1f9214fd0": ("C","","Oui, si l'autorité de police estime insuffisantes les mesures envisagées par les organisateurs."),
 "981a083c14": ("D","","Grande manifestation sous le contrôle d'un OPJ : on peut accepter (employeur engagé). (à confirmer)"),
 "671e5c2af2": ("D","","Refus de se dessaisir d'objets dangereux : refuser l'accès conformément aux consignes."),
 "ebce098b76": ("C","","« Sous le contrôle d'un OPJ » : OPJ désigné par le préfet, en situation d'astreinte."),
 "360d3e6ba9": ("B","","Après une appréhension pour vol, obligation d'appeler les forces de l'ordre."),
 "43592a49d6": ("E","","Inspection du véhicule avec le consentement du conducteur, par un APS placé sous l'autorité d'un OPJ."),
 "f6f15ae163": ("D","","Inspection du véhicule avec le consentement du conducteur, par un APS placé sous l'autorité d'un OPJ. (à confirmer — question dégradée)"),
 "5d4689e9bd": ("C","","La palpation ne se fait qu'avec l'accord de la personne, sauf état de nécessité."),
 "6f91d5de85": ("C","","Personne de même sexe, consentement exprès, sous le contrôle d'un OPJ. (à confirmer)"),
 "2b3dafe165": ("E","","Notamment : sous le contrôle d'un OPJ et sur une personne de même sexe. (à confirmer)"),
 "5b238db034": ("C","","Personne de même sexe, consentement exprès, sous le contrôle d'un OPJ."),
 "aa1959b011": ("A","","Même sexe, accord de la personne, habilitation de l'employeur et agrément."),
 "a7dc0a8d8b": ("D","","Mettre à disposition des forces de l'ordre tous les éléments nécessaires à leur intervention."),
 "f0b925fa28": ("C","","Risque principal d'un rassemblement sportif : les débordements des supporters."),
 "55efa8f633": ("E","","Palpation interdite entre sexes différents : une femme vérifie un homme au magnétomètre. (à confirmer)"),
 "a6e96b497f": ("E","","Palpation/fouille interdites entre sexes différents : aucune des méthodes proposées. (à confirmer)"),
 "af5a3f3dd0": ("A","","En circonstances exceptionnelles, l'agrément de palpation est donné par le préfet du département."),
 "0b35f0cacd": ("D","","Oui si +300 personnes, sous le contrôle d'un OPJ et sur une personne de même sexe."),
 "62b8e80ca7": ("D","","Palpation à l'entrée d'un magasin : seulement si un arrêté préfectoral le prescrit."),
 "b0e513aa76": ("B","","Gala de 200 personnes : refuser, la palpation n'est pas autorisée (risque de sanctions)."),
 "8919228f8d": ("B","","Gala de 200 personnes : refuser, la palpation n'est pas autorisée (risque de sanctions)."),
 "aa12553b87": ("D","","Fouille d'un casier : non, sauf en présence d'un représentant du personnel. (à confirmer)"),
 "3914f816a8": ("E","","Refus d'inspection : rappeler les conditions d'accès prévues pour le concert."),
})

# ---- RÉVISION des « à confirmer » (relecture une par une) ----
# 1) réponses révisées après relecture
REVISED = {
 "0ee6ed86be": ("C", "Doctrine « réagir » (SGDSN) : on alerte les secours une fois à l'abri, après s'être échappé/caché."),
 "fe8d7f592d": ("D", "Circonstance aggravante (art. 311-4 CP) : prendre indûment la qualité d'une personne dépositaire de l'autorité publique."),
}
# 2) ids qui restent réellement incertains ou dont la source est dégradée -> on garde « (à confirmer) »
KEEP_UNSURE = {
 "e31776a485",  # PPI/POI/PER : formulation ambiguë
 "babef3fcbc",  # délai renouvellement carte pro : 3 vs 4 mois
 "46726d97b2",  # question dégradée dans la source
 "a6dbf12153",  # « appréhender en surface de vente » : options faibles
 "36c998556c",  # armement agents de bailleur : point réglementaire pointu
 "e4015e9216",  # « personne ivre menaçante » : options peu satisfaisantes
 "8cba9e3efe",  # intitulé/option tronqués dans la source
 "981a083c14",  # palpations grande manifestation : débattable
 "f6f15ae163",  # options tronquées dans la source
 "a6e96b497f",  # vérif agent masculin/femmes : E (aucune) ou B (bagages)
}

# ---- LOT 5 : questions récupérées « Toutes les réponses… » (+ question re-parsée) ----
P.update({
 "1e853f144c": ("E","","Accès frauduleux, virus, suppression, modification : ce sont toutes des atteintes aux STAD."),
 "701d63d8d8": ("D","","Accès frauduleux, virus, suppression, modification : ce sont toutes des atteintes aux STAD."),
 "5fb71fba50": ("A","","Intonation, regard/voix/gestes, garder son calme : tout est à surveiller face à une personne agressive."),
 "2ef2664097": ("C","","Une consigne permanente peut être transmise par écrit, mail du PC, main courante ou remise en mains propres."),
 "98f3d30538": ("D","","Sur la main courante d'une ronde : anomalies, mesures prises, heure de retour, nom de l'agent."),
 "23b7399e91": ("B","","Une main courante est chronologique, datée, factuelle, informatisée ou manuscrite : toutes exactes."),
 "6c784c2f4b": ("A","","Corrosif, gaz sous pression, comburant, dangereux pour la santé : tous nécessitent un pictogramme."),
 "d5e2123489": ("C","","Le pneumothorax peut résulter d'une plaie par balle/arme blanche, d'un blast ou d'une perforation par une côte."),
 "372ea31006": ("D","","Laisser ses affaires, aider les autres à fuir, se confiner si on ne peut courir, alerter : toutes appropriées."),
 "286b712128": ("E","","Consommation non payée = vol consommé : récupérer les emballages (preuve) pour l'appréhension."),
 "65a5fe4d04": ("C","","Il existe des blasts primaire, secondaire, tertiaire et quaternaire : toutes exactes."),
 "c3aa38470d": ("D","","Le code du sport (L332-3) punit l'accès en état d'ivresse et l'introduction de boissons alcoolisées : toutes exactes."),
 "765e235aa6": ("D","","R211-23 : signe distinctif, moyens de communication avec l'OPJ, liaison permanente, copie des agréments : toutes exactes."),
 "27cd5d3b2b": ("B","","R211-23 : signe distinctif, moyens de communication avec l'OPJ, liaison permanente, copie des agréments : toutes exactes."),
 "4ca4dc5494": ("E","","R211-23 : signe distinctif, moyens de communication avec l'OPJ, liaison permanente, copie des agréments : toutes exactes."),
 "00a1a18025": ("C","","Caméras fixes, 360°, vision nocturne, lecture de plaques : tous ces types existent."),
 "c7bc4730da": ("A","","Journalistes, VIP, artistes, organisateurs : tous ces acteurs nécessitent une attention en sûreté."),
})

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # garde-fou : ne jamais écraser une clé de correction validée par le formateur
    ans_js = os.path.join(base, "app", "answers.js")
    if os.path.exists(ans_js) and "VALIDÉ PAR" in open(ans_js, encoding="utf-8").read(200):
        if "--force" not in sys.argv:
            print("⛔ app/answers.js est marqué VALIDÉ — régénération annulée "
                  "(utilise --force pour écraser volontairement).")
            return
    Q = json.load(open(os.path.join(base, "data", "questions.json"), encoding="utf-8"))
    by_id = {q["id"]: q for q in Q}
    out = {}
    missing = []
    for qid, (letter, diff, just) in P.items():
        q = by_id.get(qid)
        if not q:
            missing.append(qid); continue
        if qid in REVISED:                       # réponse revue à la relecture
            letter, just = REVISED[qid][0], REVISED[qid][1]
        if qid not in KEEP_UNSURE:               # tranché -> on retire la mention
            just = just.replace(" (à confirmer — question dégradée)", "").replace(" (à confirmer)", "")
        idx = "ABCDE".index(letter)
        if idx >= len(q["options"]):
            missing.append(qid+"(idx)"); continue
        rec = {"answer": idx, "justification": just}   # difficulté supprimée
        if q.get("uv") is not None:
            rec["uv"] = q["uv"]
        out[qid] = rec
    # write answers.js
    with open(os.path.join(base, "app", "answers.js"), "w", encoding="utf-8") as fh:
        fh.write("window.QCU_ANSWERS = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
    # also keep a json copy
    with open(os.path.join(base, "data", "answers.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"Propositions écrites : {len(out)} / {len(P)}  (manquantes: {missing})")

if __name__ == "__main__":
    main()
