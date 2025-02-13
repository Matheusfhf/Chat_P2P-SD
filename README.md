# P2P Chat - Comunicação em Rede Local

Este projeto é um chat peer-to-peer (P2P) que permite a comunicação entre computadores diferentes na mesma rede local. Ele utiliza um Super Peer (Tracker) para registrar e listar os participantes.

## Requisitos

- Python 3.x instalado
- Computadores conectados à mesma rede local

## Configuração e Execução

### 1. Iniciar o Super Peer (Tracker)
O Super Peer é responsável por registrar os peers conectados. Você precisa executá-lo primeiro em um computador que servirá como servidor.

#### Passos:
1. **Descubra o IP local do computador do Super Peer:**
   - **Windows**: Abra o Prompt de Comando e digite:
     ```sh
     ipconfig
     ```
   - **Linux/macOS**: Abra o terminal e digite:
     ```sh
     ifconfig  # ou
     ip a
     ```
   - O IP será algo como `192.168.x.x`.

2. **Edite o código do Super Peer**: No arquivo do código em anexo 'P2PChat.py', altere a linha 6:
   ```python
   tracker_host = "127.0.0.1"
   ```
   ![Ip Terminal](assets/image.png)

   Para o IP do computador que está rodando o Super Peer, por exemplo:
   ```python
   tracker_host = "192.168.0.207"
   tracker_port = 5050
   ```

3. **Execute o código do Super Peer**:
   ```sh
   python3 P2PChat.py
   ```
   Agora, o Super Peer está rodando e pronto para registrar os peers.

---

4. **Escolha seu usuário e a porta de sua conexão**:
![Servidor rodando](assets/image-2.png)

### 2. Iniciar os Peers (Usuários do Chat)
Cada usuário do chat precisa executar o código em seu computador e se conectar ao Super Peer.

#### Passos:
1. **Descubra o IP local do computador do Peer** (mesmo processo do Super Peer).

2. **Edite o código do Peer** para apontar para o Super Peer, alterando:
   ```python
   tracker_host = "127.0.0.1"
   ```
   Para o IP do Super Peer:
   ```python
   tracker_host = "192.168.0.207"
   tracker_port = 5050
   ```

3. **Execute o código do Peer**:
   ```sh
   python3 chat.py
   ```

4. **Digite as informações quando solicitado:**
   - Escolha um **nome de usuário**.
   - Insira o **IP local** do seu próprio computador.
   - Escolha uma **porta** para conexão (exemplo: `12345`).

---

![Segundo PC](assets/image-3.png)

### 3. Conectar os Peers ao Chat
Após os peers estarem registrados no Super Peer, siga estes passos:

1. Clique no botão **"Atualizar Peers"** para listar os usuários conectados.
2. Selecione um usuário na lista.
3. Clique no botão **"Conectar ao Peer"** para iniciar o chat.

![Interface](assets/image-4.png)

Agora os usuários podem trocar mensagens em tempo real!

## Possíveis Erros e Soluções

- **Erro de conexão:** Verifique se o IP do Super Peer está correto e se o firewall não está bloqueando as conexões.
- **Peers não aparecem na lista:** Certifique-se de que o Super Peer está rodando e que os peers se registraram corretamente.
- **Conexão recusada:** Tente usar portas diferentes para cada peer.

---
Para maiores instruções de implementação acesse o PDF do relatório presente na pasta.
---
Desenvolvido por João Marcelo Rossi, Matheus Freire e Rafael Assunção

