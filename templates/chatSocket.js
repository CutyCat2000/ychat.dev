let chatSocket;
const serverURL = "wss://" + window.location.host + "/";

function connectWebSocket() {
  chatSocket = new WebSocket(serverURL);
  chatSocket.onopen = function (e) {
    console.log("WebSocket connection established");
  };
  chatSocket.onclose = function (e) {
    console.log("WebSocket connection closed unexpectedly");
    setTimeout(connectWebSocket, 3000);
  };
  chatSocket.onmessage = function (e) {
    console.log("Received message:", e.data);
    const data = JSON.parse(e.data);
    if (data["option"] == "error") {
      alert(data["message"]);
    } else if (data["option"] == "send_message") {
      const timestamp = new Date(data["timestamp"]);
      const options = {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
        hour12: true,
        timeZone: "UTC",
      };
      const formattedTime = new Intl.DateTimeFormat("en-US", options).format(timestamp);
      const formattedTimeUTC = formattedTime.replace(" at", "").replace("AM", "a.m.").replace("PM", "p.m.").replace(":00", "") + " UTC";
      if (data["serverId"] == serverId && data["channelId"] == channelId) {
        if (!document.hasFocus()) {
          new Notification(`${data["message_author"]["name"]} in ${data["serverName"]} (#${data["channelName"]})`, {body:data["message_content"],icon:"https://cdn-icons-png.flaticon.com/512/6405/6405847.png", image:data["attachments"][0]});
        }
        const newMessageElement = document.createElement('div');
        newMessageElement.classList.add('message');
        newMessageElement.id = data["message"];
        USER_ID = document.getElementsByClassName('self-id')[0].id
        // setContextMenu('message',MESSAGE_ID, AUTHOR_ID, USER_ID)
        newMessageElement.setAttribute('onmousedown', `setContextMenu('message',${data["message"]}, ${data["message_author"]["id"]}, ${USER_ID})`);
        newMessageElement.innerHTML = `
          <div class="message-author" id="${data["message"]}">
            <span class="message-author-name" id="${data["message_author"]["id"]}">
              ${data["message_author"]["name"]}
            </span>
            <span class="timestamp">
              ${formattedTime.trim()}
            </span>
          </div>
          <div class="message-content">
            <span>${data["message_content"]}</span>
            <div class="message-attachments">
              ${data["attachments"].map(attachment => `
              <img src="${attachment}" alt="Embedded link">
              `).join('')}
            </div>
            <div class="reactions"><button class="reaction-button" onclick="openEmojiPicker(${data["message"]}, '/channel/${serverId}/${channelId}/update_reaction/${data["message"]}/')">+</button></div>
          </div>
        `;
        const chatElement = document.querySelector('.chat');
        chatElement.insertBefore(newMessageElement, chatElement.firstChild);
      }
      else {
        new Notification(`${data["message_author"]["name"]} in ${data["serverName"]} (#${data["channelName"]})`, {body:data["plain_message_content"],icon:"https://cdn-icons-png.flaticon.com/512/6405/6405847.png", image:data["attachments"][0]});
      }
    } else if (data["option"] == "edit_message") {
      const data = JSON.parse(e.data);
      const messageElements = document.getElementsByClassName('message');
      let messageElement = null;
      for (let i = 0; i < messageElements.length; i++) {
        if (messageElements[i].id === data["messageId"].toString()) {
          console.log('ok');
          messageElement = messageElements[i].querySelector('.message-content span');
          break;
        }
      }
      if (messageElement) {
        messageElement.innerHTML = data["message_content"]+'<small><small style="color: lightblue">[EDITED]</small></small>';
        attachmentsElement = messageElement.querySelector('.message-attachments');
        if (attachmentsElement) {
          attachmentsElement.innerHTML = '';
          data["attachments"].forEach(attachment => {
            const img = document.createElement('img');
            img.src = attachment;
            img.alt = 'Embedded link';
            attachmentsElement.appendChild(img);
          });
        } else {
          const attachmentsElement = document.createElement('div');
          attachmentsElement.classList.add('message-attachments');
          data["attachments"].forEach(attachment => {
            const img = document.createElement('img');
            img.src = attachment;
            img.alt = 'Embedded link';
            attachmentsElement.appendChild(img);
          });
          messageElement.appendChild(attachmentsElement);
        }
      }
    } else if (data["option"] == "delete_message") {
      const data = JSON.parse(e.data);
      const messageElements = document.getElementsByClassName('message');
      let messageElement = null;
      for (let i = 0; i < messageElements.length; i++) {
        if (messageElements[i].id === data["messageId"].toString()) {
          messageElement = messageElements[i];
          break;
        }
      }
      if (messageElement) {
        messageElement.remove();
      }
    } else if (data["option"] == "create_reaction") {
      const data = JSON.parse(e.data);
      const messageElements = document.getElementsByClassName('message');
      let messageElement = null;
      for (let i = 0; i < messageElements.length; i++) {
        if (messageElements[i].id === data["messageId"].toString()) {
          messageElement = messageElements[i];
          break;
        }
      }
      if (messageElement) {
        const reactionElement = document.createElement('button');
        reactionElement.classList.add('reaction-button');
        reactionElement.onclick = () => {
          updateReaction(data["reaction"], data["messageId"]);
        }
        reactionElement.innerHTML = `${data["reaction"]} (${data["counter"]})`;
        // Add before last child
        messageElement.querySelector(
          '.message-content .reactions').insertBefore(reactionElement, messageElement.getElementsByClassName('reaction-button')[messageElement.getElementsByClassName('reaction-button').length - 1]);
      }
    } else if (data["option"] == "delete_reaction") {
      const data = JSON.parse(e.data);
      const messageElements = document.getElementsByClassName('message');
      let messageElement = null;
      for (let i = 0; i < messageElements.length; i++) {
        if (messageElements[i].id === data["messageId"].toString()) {
          messageElement = messageElements[i];
          break;
        }
      }
      if (messageElement) {
        const reactionElements = messageElement.querySelectorAll('.reaction-button');
        let reactionElement = null;
        for (let i = 0; i < reactionElements.length; i++) {
          if (reactionElements[i].innerHTML.includes(data["reaction"])) {
            reactionElement = reactionElements[i];
            break;
          }
        }
        if (reactionElement) {
          reactionElement.remove();
        }
      }
    } else if (data["option"] == "add_reaction" || data["option"] == "remove_reaction") {
      const data = JSON.parse(e.data);
      const messageElements = document.getElementsByClassName('message');
      let messageElement = null;
      for (let i = 0; i < messageElements.length; i++) {
        if (messageElements[i].id === data["messageId"].toString()) {
          messageElement = messageElements[i];
          break;
        }
      }
      if (messageElement) {
        const reactionElements = messageElement.querySelectorAll('.reaction-button');
        let reactionElement = null;
        for (let i = 0; i < reactionElements.length; i++) {
          if (reactionElements[i].innerHTML.includes(data["reaction"])) {
            reactionElement = reactionElements[i];
            break;
          }
        }
        if (reactionElement) {
          reactionElement.innerHTML = `${data["reaction"]} (${data["counter"]})`;
        }
      }
    }
  };
}


function sendMessage() {
    chatInput = document.getElementById("chat-input");
    message = chatInput.value
    if (message.replaceAll(" ","") != "") {
      console.log("bye");
      context = {
        option: "send_message",
        message: message,
        serverId: serverId,
        channelId: channelId,
      };
      chatSocket.send(JSON.stringify(context));
      chatInput.value="";
    }
}

function editMessage() {
  chatInput = document.getElementById("chat-input");
  message = chatInput.value
  if (message.replaceAll(" ","") != "") {
    console.log("bye");
    context = {
      option: "edit_message",
      messageId: messageId,
      message: message,
      serverId: serverId,
      channelId: channelId,
    }
    chatSocket.send(JSON.stringify(context));
    chatInput.value="";
  }
}

function deleteMessage() {
  if(confirm("Do you really want to delete this message?")) {
    context = {
      option: "delete_message",
      messageId: messageId,
      serverId: serverId,
      channelId: channelId,
    }
    chatSocket.send(JSON.stringify(context));
  }
}

function updateReaction(emoji, messageId) {
  context = {
    option: "update_reaction",
    reaction: emoji,
    messageId: messageId,
    serverId: serverId,
    channelId: channelId,
  }
  chatSocket.send(JSON.stringify(context));
}







connectWebSocket();