# AMS - SmartParking
Implementação do protótipo funcional em ambiente web, disponivel em [servidor online](https://ams-smartparking.herokuapp.com/).

## Como utilizar

1. **Iniciar sessão**
 * Criar uma nova conta, utilizando a opção `Registar`
 * Utilizar uma conta já existente, utilizando a opção `Entrar`
2. **Reservar parque**

 Utilizar o botão `Procurar estacionamento` para aceder à página onde pode escolher no mapa o parque de estacionamento pretendido e finalizar com o botão `Reservar`

3. **Autenticar entrada**

 Utilizar o botão `Autenticar entrada/saída` para visualizar o *QRCode* associado à reserva. O botão `Início do estacionamento` simula o reconhecimento do *QRCode* à entrada do parque, e inicia a contagem do tempo de estacionamento.

4. **Autenticar saída**

 Utilizar o botão `Autenticar entrada/saída` para visualizar o *QRCode* associado à reserva. O botão `Fim do estacionamento` simula o reconhecimento do *QRCode* à saída do parque, e termina a contagem do tempo de estacionamento.

 *É apresentada uma página informativa com o **parque** utilizado e o **tempo** de estacionamento.*

5. **Navegação**

 Utilize os botões `Voltar` para regressar à página anterior. Utilize o botão `Sair` para terminar sessão na conta ativa.

## Como testar

Conta "teste" já criada (utilização facultativa):
> **Utilizador:** teste@test.t
**Palavra-passe:** teste

* Parque de estacionamento livre  
 Os parques *Saba Marquês de Pombal* e *do Fórum Aveiro* têm um número elevado de lugares disponíveis.
* Parque de estacionamento lotado  
 O parque *Nossa Sra. dos Aflitos* não tem lugares disponíveis.
* Registo e verificação de dados  
 O parque *UA* tem apenas um lugar disponível. Pelo que, se um utilizador reservar esse lugar, enquanto a reserva estiver ativa, outro utilizador não poderá reservar um lugar neste parque, sendo notificado que está lotado.

Quando uma reserva está ativa, é apresentado o nome do parque e o tempo decorrido até ao momento (se este já tiver autenticado entrada) no menu `Início` e `Autenticar entrada/saída`.

O botão `Testar API do gerador de QRCodes` apresenta uma página onde se pode ver o *QRCode* possível de ser gerado (e a informação contida - *String*), com o nome de utilizador, nome do parque de estacionamento da reserva e um número aleatório.

### Funcionalidades implementadas

- [x] Pesquisa de parque através de um mapa interativo
- [ ] Pesquisa de parque através de reconhecimento da localização atual
- [x] Leitura e escrita de informação na base de dados em tempo real, permanente e coerente entre várias sessões
- [x] Contagem do tempo de estacionamento
- [ ] Possibilidade de associar a conta a uma conta *PayPal* ou *ViaVerde*
- [ ] Processamento do pagamento acedendo a uma conta *PayPal* ou *ViaVerde*
- [ ] Possibilidade de avaliar parques de estacionamento frequentados, e visualização dos seus *ratings* dados pelos utilizadores