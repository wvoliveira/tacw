[![build status](https://travis-ci.org/wvoliveira/tacw.svg?branch=master)](https://travis-ci.org/wvoliveira/tacw)

Tag Cloud Worker
----------------

Worker para coletar informações do [TrackSale.co](https://tracksale.co/) e do chat Orbium pelo Atende.

### Como funciona?


1 - Antes de tudo é necessário ter o arquivo .env.ini para o script carregar as informações necesśarias  
2 - Agora coleto informações do TrackSale através dessa URL: https://tracksale.co/live/key_here/comments  

A saída será parecida com essa:  
```json
[{...
    "name":"Gilmar Lopes",
    "phone":"(11) 0000-0000",
    "reminder_time":null,
    "nps_comment":"varios curriculos enviados e nenhum contato, n\u00e3o compensa, por isso ja fiz o cancelamento agendado e nunca mais vou usar os servi\u00e7oes de voces",
    "time":1505997357,
    "nps_answer":0,
    "dispatch_time":null
},
```

A parte que nos importa é o 'nps_comment', mas para criar o tag cloud preciso transformar isso numa lista de palavras. Ficando assim:  
```json
"comment_split":["varios","curriculos","enviados","e","nenhum","contato,","n\u00e3o","compensa,","por","isso","ja","fiz","o","cancelamento","agendado","e","nunca","mais","vou","usar","os","servi\u00e7oes","de","voces"]
```

O que eu faço aqui é simplesmente criar uma nova chave no dicionário, mantendo a original para um uso futuro no Kibana.

3 - Hora de coletar informações do Chat Orbium - clientes do site atendidos pelo Chat Online. Os comentários do chat está no **internoslave.vs** na tabela **reclamacao**.  
A lógica continua a mesma: coleto o comentário cru e converto para uma lista de palavras, removendo pontos e vírgula:  

```json
"comment_split":["Eu","era","cliente","da","Catho","por","20","anos","Na","renova\u00e7\u00e3o","do","contrato","deu","problema","por","que","meu","cart\u00e3o","foi","clonado","Junto","com","isto","comecei","a","receber","dezenas","de","liga\u00e7\u00f5es","da","empresa","e","pedi","para","pararem","Como","n\u00e3o","aconteceu","fiz","o","cancelamento","imediato","conforme","meu","contrato","Tenho","um","d\u00e9bito","de","RS$1875","coma","empresa","e","gostaria","de","que","vcs","emitissem","um","boleto","visto","que","meu","cart\u00e3o","foi","clonado","e","ainda","n\u00e3o","recebi","o","novo","Obrigado","!"]
```

Como existem pequenas palavras, preciso remover da núvem de palavras. Seria legal ignorar palavras pequenas (TODO). 
O Kibana até tem um campo 'exclude' nas configurações da visualização tag cloud, mas acredito que dentro do código ficará mais eficaz, se não teremos que adicionar cada palavra nova na lista. Exemplo:  
```
a|A|/>|as|Em|do|meu|das|Há|e|o|etc|está|é:|Não|em|estão|2|gostei|de|para|me|3|99%|Do|pra|por|com|tive|não|um|no|0|1|7|!|que|mas|uma|da|eu|Att|se|já|ter|o|ou|Olá|O|As|aqui|caso|fiz|Sei|As|20|ao|foi|é
```
