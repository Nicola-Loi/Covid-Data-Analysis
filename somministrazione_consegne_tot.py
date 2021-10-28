
import pandas as pd

#Importo i dati da GitHub
url_somministrazioni = 'https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-latest.csv'
url_consegne = 'https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/consegne-vaccini-latest.csv'
df_somministrazioni = pd.read_csv(url_somministrazioni, error_bad_lines = False)
df_consegne = pd.read_csv(url_consegne, error_bad_lines = False)

# Analisi del DataSet Somministrazioni
#Info sui campi e sulla tipologia degli elementi
print('Informazioni DataSet Somministrazioni-vaccini-latest: Campi/Type/Null/Valori differenti per campo')
df_somministrazioni.info()
print('\n')
#Check su elementi differenti in ogni campo
print(df_somministrazioni.nunique())
print('\n')

# Analisi del DataSet Consegne
#Info sui campi e sulla tipologia degli elementi
print('Informazioni DataSet Consegne-vaccini-latest: Campi/Type/Null/Valori differenti per campo')
df_consegne.info()
print('\n')
#Check su elementi differenti in ogni campo
print(df_consegne.nunique())
print('\n')

#Pulisco il dataset eliminando i campi ridondanti
df_somministrazioni = df_somministrazioni.drop(['area','codice_NUTS1','codice_NUTS2','codice_regione_ISTAT'],axis=1)
df_consegne = df_consegne.drop(['area','codice_NUTS1','codice_NUTS2','codice_regione_ISTAT'],axis=1)

#Cambio le date object in datetime
df_somministrazioni.data_somministrazione = pd.to_datetime(df_somministrazioni.data_somministrazione)
df_consegne.data_consegna = pd.to_datetime(df_consegne.data_consegna)

#Qualche statistica rilevante
print('Data consegne più recenti: ',df_consegne.data_consegna.min().date() ,'- Ultime consegne registrate: ',df_consegne.data_consegna.max().date())
print('Data somministrazioni più recenti: ',df_somministrazioni.data_somministrazione.min().date() ,'- Ultime somministrazioni registrate: ',df_somministrazioni.data_somministrazione.max().date())
print('Totale Dosi Consegnate: ', df_consegne['numero_dosi'].sum())
print('Totale con almeno una dose: ', df_somministrazioni['prima_dose'].sum())
print('Totale ciclo vaccinale: ', df_somministrazioni['seconda_dose'].sum())
print('Totale dose addizionale: ', df_somministrazioni['dose_aggiuntiva'].sum())
print('Totale richiamo(booster): ', df_somministrazioni['dose_booster'].sum())
print('Totale somministrazioni: ', df_somministrazioni['prima_dose'].sum()+
                            df_somministrazioni['seconda_dose'].sum()+
                                df_somministrazioni['dose_aggiuntiva'].sum()+
                                df_somministrazioni['dose_booster'].sum())

# Pulisco il dataset da ciò che non mi serve
df_somministrazioni = df_somministrazioni.drop(['data_somministrazione','fornitore','fascia_anagrafica','sesso_maschile','sesso_femminile','pregressa_infezione'],axis=1)
df_consegne = df_consegne.drop(['fornitore','data_consegna'],axis=1)

#Creo il dataframe per il report
somministrazioni_regione = {}
consegne_regione ={}
percentuale_regione = {}
for nome_area in df_somministrazioni.nome_area.unique() : 
    vaccinati = 0
    consegne = 0
    percentuale = 0
    
    vaccinati = df_somministrazioni.loc[df_somministrazioni['nome_area'] == nome_area, 'prima_dose'].sum()+\
                df_somministrazioni.loc[df_somministrazioni['nome_area'] == nome_area, 'seconda_dose'].sum()+\
                df_somministrazioni.loc[df_somministrazioni['nome_area'] == nome_area, 'dose_aggiuntiva'].sum()+\
                df_somministrazioni.loc[df_somministrazioni['nome_area'] == nome_area, 'dose_booster'].sum()
    consegne = df_consegne.loc[df_consegne['nome_area'] == nome_area, 'numero_dosi'].sum()
    percentuale = (vaccinati/consegne)*100
    
    consegne_regione[nome_area] = consegne 
    somministrazioni_regione[nome_area] = vaccinati
    percentuale_regione [nome_area] = percentuale

    somministrazioni_regione_df = pd.DataFrame.from_dict(somministrazioni_regione, orient='index', columns = ['Dosi somministrate']).reset_index()
    consegne_regione_df = pd.DataFrame.from_dict(consegne_regione, orient='index', columns = ['Dosi consegnate']).reset_index()
    percentuale_regione_df = pd.DataFrame.from_dict(percentuale_regione, orient='index', columns = ['%']).reset_index()

#Concateno e setto colonne
report = pd.concat([somministrazioni_regione_df,
            consegne_regione_df['Dosi consegnate'],
            percentuale_regione_df['%']], axis = 1)
report.rename(columns = {'index':'Regioni'}, inplace = True)

#Creo il CSV
report.to_csv('somministrazione-consegne-tot.csv', index = False) 
