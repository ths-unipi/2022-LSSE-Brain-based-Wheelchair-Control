"waiting_for_dataset":
    Il DS si avvia e si mette in attesa di un dataset. Una volta letto dalla coda lo salva nel database, cambia in operational mode "early_training" e avvia 
    l'early training controller. L'early training controller setta gli average parameters, fa il training, esporta il report, cambia modalità a 
    "check_early_training_report" e si spegne.

"early_training": (se il ssitema cracha nell'early training)
    l DS crea l'early training controller che setta gli average parameters, fa il training, esporta il report, cambia modalità a 
    "check_early_training_report" e si spegne.

"check_early_training_report":
    Il DS si avvia e legge il report dell'early training. Se il numero delle generazioni non è buono riparte dall'early training, mentre se è buono
    crea il grid search controller. Questo va a fare la grid search e alla fine esporta il report dei top five best classifiers, cambia
    modalità in "check_top_five_report" e si spegne.

"check_top_five_report":
    Il DS si avvia e legge il report. Se non c'è un actual best riparte dall'early training, se c'è avvia crea il test best class. controller
    che testa il classificatore e crea il report, cambia modalità in "check_test_report" e si spegne.

"check_test_report":
    Il DS si avvia e legge il report il report, se è ok si invia all'execute altrimenti si riparte e basta. 
    In entrambi i casi si ritora a "waiting_for_dataset" e viene svuotato il dataset.

possibili operational_mode = ["waiting_for_dataset", "early_training", "check_early_training_report", "check_top_five_report", "check_test_report"]