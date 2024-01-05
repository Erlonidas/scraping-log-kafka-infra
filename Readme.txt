Este é um exemplo de aplicação da linguagem python, para realizar um scrap em um log.txt, considerando que 
esse log é recebido via um servidor de mensagenria, como o Kafka. As APIs  são armazenadas localmente em
containers docker, em banco noSQL (mongoDB). Seja bem vindo. 

A aplicação recebe um extenso log contendo informações de horas, e movimentações de jogadores em um game
de FPS (como CS, Vava, CoD, The Arena 3). Informações de cada rodada feita no lobby do game são registrados
e a aplicação em python extrai informações importantes tanto para registro do que cada jogador fez, quanto 
para futuras analises de comportamento do jogadores na sala.

### How it works:

<i> Kafka </i> || <i> Docker </i> || <i> MongoDB </i>  
É separado o Zookeeper e um broker Kafka em containers para gestão de eventos disparados por 1 producer, 
enquanto o 1 consumer coleta as mensagens. Nesse repositorio, no arquivo para sendLog.py é criado uma instancia 
do producer, para enviar o arquivo de log para o servidor, em uma porta específicada no docker-compose, 
enquanto o arquivo main.py cria a instancia do consumer, que coleta as informações que sao registradas após 
a sua criação.
Após obter as informações, é realizado o scrapping, e os dados são armazenados em documentos no MongoDB.

Na pasta 'modules' contém as classes responsáveis pelo scrapping, e controllers estão as classes responsaveis
por lidar com a API do Kafka-Confluent, e o MongoDB. Na pasta de testes estão os testes unitários das classes 
em 'module' usando o framework Pytest. Um resumo dos testes unitários estão disponíveis em arquivos .html

#### How to use:

1) Clone o repositorio.

2) Instale os pacotes que estão no requirements usando.
>> pip install -r requirements.txt

3) Execute o docker-compose. Voce deve ter 3 containers ativos.
>> docker-compose -d up

3.1) Entre no broker, e configure as repartições e o tópico para conectar com o consumer.
O nome do broker no arquivo .yml é "only1Brokerv2".

>> docker exec -it "broker_name" bash
>> docker-topics --create --bootstrap-server "url broker" --replication-factor 1 --partition 1 --topic "topic_name"

A nivel de exemplo, tanto o fator de replicação quando as partições foram configurados para 1. Para aplicações
a nivel comercial, é recomendado usar mais de 1 broker, com replicações e partições acima de 2.

Se quiser checar se o tópico foi criado: 
>> kafka-topics --list --bootstrap-server localhost:"url broker"

4) O consumer foi instanciado no arquivo main.ipynb, assim fica mais didático observar cada passo do scrapping.
Lembre de instanciar o consumer antes de executar o producer no step 5. 

5) Abra o seu terminal, e execute o arquivo 'kafka-docker/testes_in_project/sendLog.py
>> python sendLog.py localhost:19092 "your-topic-here"

6) Go back to file main.ipynb, and continue running each cell.










