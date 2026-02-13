# Documentazione Architetturale

## Introduzione
Questa documentazione descrive l'architettura del sistema e i suoi componenti principali. Include i diagrammi UML per visualizzare l'architettura in modo chiaro e comprensibile.

## Diagramma del Contesto
![Diagramma del Contesto](../diagrams/context_diagram.png)

Il diagramma del contesto mostra le interazioni principali tra i componenti del sistema e gli attori esterni. In particolare, gli utenti interagiscono con il **Web Server**, che a sua volta comunica con l'**Application Server** e il **Database Server**.

\newpage
## Diagramma dei Componenti
![Diagramma dei Componenti](../diagrams/component_diagram.png)

Il diagramma dei componenti rappresenta le entità principali del sistema, come il **Catalog Service**, il **Cart Service**, e l'**Order Service**, e le loro interazioni.

## Diagramma del Deployment
![Diagramma del Deployment](../diagrams/deployment_diagram.png)

Il diagramma del deployment mostra come i vari componenti sono distribuiti nei nodi del sistema, come il **Web Server** e il **Database Server**.

\newpage
## Diagramma di Sequenza
![Diagramma di Sequenza](../diagrams/sequence_diagram.png)

Il diagramma di sequenza mostra l'interazione temporale tra i vari componenti, come il **Cart Service**, **Order Service**, e **Payment Service**.

\newpage
## Diagramma di Sicurezza
![Diagramma di Sicurezza](../diagrams/security_diagram.png)

Il diagramma di sicurezza illustra le misure di sicurezza tra i vari componenti, come la cifratura SSL/TLS e i controlli di accesso tra il **Web Server**, il **Application Server** e il **Database Server**.

## Conclusione
In questa documentazione, abbiamo analizzato l'architettura del sistema, descrivendo i principali componenti e le loro interazioni. I diagrammi generati forniscono una visione chiara e comprensibile dell'architettura, evidenziando le relazioni tra i vari componenti e le misure di sicurezza adottate. Questo documento sarà un riferimento utile per comprendere come i vari servizi lavorano insieme per fornire una soluzione scalabile e sicura.