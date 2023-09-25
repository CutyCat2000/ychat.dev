if ('Notification' in window){
  console.log(Notification.permission)
  if (Notification.permission != "granted") {
    Notification.requestPermission().then(function (permission) {});
  }
}

function getChannelIdsFromUrl() {
  const urlParts = window.location.pathname.split('/');
  let serverId, channelId;
  if (urlParts[1] == "dm") {
    serverId = "dm";
    channelId = urlParts[2];
  } else {
    serverId = urlParts[2];
    channelId = urlParts[3];
  }
  return { serverId, channelId };
}

const { serverId, channelId } = getChannelIdsFromUrl();

function scrollChat(message) {
    //document.getElementsByClassName("chat")[0].scrollTop = message.offsetHeight + message.offsetTop; 
}

function sendMessage() {
    chatInput = document.getElementById("chat-input");
    message = encodeURIComponent(chatInput.value);
    console.log(message);
    console.log(chatInput.innerHTML);
    console.log(chatInput.innerText);
    if (message.replaceAll(" ","") != "") {
      console.log("bye");
        window.open('/channel/'+serverId+'/'+channelId+'/send_message?content='+message, target="_self");
    }
}

messageId = ""
try {
  userId = parseInt(document.getElementsByClassName("self-id")[0].id);
  serverOwnerId = parseInt(document.getElementsByClassName("server-owner-id")[0].id);
} catch(es) {
  
}

function editMessage() {
    chatInput = document.getElementById("chat-input");
    message = encodeURIComponent(chatInput.value);
    console.log(message);
    console.log(chatInput.innerHTML);
    console.log(chatInput.innerText);
    if (message.replaceAll(" ","") != "") {
      console.log("bye");
        window.open('/channel/'+serverId+'/'+channelId+'/edit_message/'+messageId+'?content='+message, target="_self");
    }
}

function deleteMessage() {
  if(confirm("Do you really want to delete this message?")) {window.open('/channel/'+serverId+'/'+channelId+'/delete_message/'+messageId, target="_self");
  }
}

window.onmousedown = function() {
    e = window.event;
    clickedElement = e.target;
    var contextMenu = document.getElementById("context-menu");
    contextMenu.style.display = "none";
    if (e.button == 0) {
        if (clickedElement.className == "server") {
            server_id = clickedElement.id;
            if (server_id == "dm") {
                window.open("/", target="_self");
            } else {
                window.open("/server/"+server_id, target="_self");
            }
        }
        if (clickedElement.className == "channel-name" || clickedElement.className == "channel-box") {
            if (clickedElement.className == "channel-name") {
                channel_id = clickedElement.parentNode.id;
                window.open("/channel/"+channel_id, target="_self");
            } else {
                channel_id = clickedElement.id;
                window.open("/channel/"+channel_id, target="_self");
            }
        }
        if (clickedElement.className == "dm-name" || clickedElement.className == "dm-box") {
            if (clickedElement.className == "dm-name") {
                channel_id = clickedElement.parentNode.id;
                window.open("/dm/"+channel_id, target = "_self");
            } else {
                channel_id = clickedElement.id;
                window.open("/dm/"+channel_id, target = "_self");
            }
        }
        if (clickedElement.className == "settings-icon") {
            window.open("/user/settings",target="_self");
        }
        if (clickedElement.className == "server-title" && clickedElement.id != "dms") {
            server_id = clickedElement.id;
            window.open("/server/settings/"+server_id,target="_self");
        }
        if (clickedElement.id == "chat-send") {
            sendMessage();
        }
        if (clickedElement.className == "message-author-name") {
            channel_id = clickedElement.id;
                window.open("/dm/create/"+channel_id, target = "_self");
        }
    }
}

window.onkeydown = function() {
    e = window.event;
    if (e.target.id == "chat-input" && e.key == "Enter") {
        sendMessage();
    }

}

window.onload = function() {
    messages = document.getElementsByClassName("message");
    message = messages[messages.length - 1];
    scrollChat(message);
}

function setContextMenu(typeOfMenu, forID, authorID = null, userID = null) {
    if (window.event.button == 2) {
      if (typeOfMenu == "message"){
        if (window.event.shiftKey) {
          if (userID == serverOwnerId || userID == authorID) {
            messageId = forID
            deleteMessage();
          }
        }
        else if (userID == authorID) {
          messageId = forID;
          document.getElementById("chat-input").value = prompt("Edit your message:");
          editMessage();
        }
      }
      else {
      }
    }
    // var contextMenu = document.getElementById("context-menu");
    // contextMenu.style.display = "block";
}

function showContextMenu(e) {
    var contextMenu = document.getElementById("context-menu");
    contextMenu.style.left = e.clientX + "px";
    contextMenu.style.top = e.clientY + "px"
    e.preventDefault();
    clickedElement = e.target;
    if (clickedElement.className == "server") {
        server_id = clickedElement.id;
        if (server_id != "dm") {
            setContextMenu("server", server_id)
        }
    }
    if (clickedElement.className == "dm-name" || clickedElement.className == "dm-box") {
        if (clickedElement.className == "dm-name") {
            channel_id = clickedElement.parentNode.id;
            setContextMenu("user", channel_id)
        } else {
            channel_id = clickedElement.id;
            setContextMenu("user", channel_id)
        }
    }
    if (clickedElement.className == "server-title" && clickedElement.id != "dms") {
        server_id = clickedElement.id;
        setContextMenu("server", server_id)
    }
}

function areThereNewMessagesCheck() {
  fetch('/channel/latest/' + userId, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': '{{ csrf_token }}',
    },
    credentials: 'include',
  })
    .then((response) => response.json())
    .then((data) => {
      for (const server of data.servers) {
        for (const channel of server.channels) {
          const storageKey = `channel_${channel.id}`;
          var storedMessageId = localStorage.getItem(storageKey);
          try {
            storedMessageId.toString();
          }
          catch (error) {
            storedMessageId = "0";
          }

          if (storedMessageId.toString() != channel.message_id.toString() && storedMessageId.toString() != channel.message_id.toString() + "-read") {
            localStorage.setItem(storageKey, channel.message_id);
            if (channel.id.toString() === channelId.toString() && window.location.pathname.includes("channel")) {
              if (!document.hasFocus()) {
                new Notification("New message", {body:"New message",icon:"https://cdn-icons-png.flaticon.com/512/6405/6405847.png"})
              }
            } else {
              new Notification("New message", {body:"New message",icon:"https://cdn-icons-png.flaticon.com/512/6405/6405847.png"})
            }
          } else if (!storedMessageId.endsWith('-read')) {
            if (channel.id.toString() === channelId.toString() && window.location.pathname.includes("channel")) {
              localStorage.setItem(storageKey, `${channel.message_id}-read`);
              document.getElementById(server.server_id).style["outline"] = "none";
              console.log("Message now read in "+server.server_id);
            }
            else {
              document.getElementById(server.server_id).style["outline"] = "3px solid white";
              console.log("Message still unread in "+server.server_id)
            }
          }
        }
      }
      for (const dm of data.dms) {
        const storageKey = `dm_${dm.id}`;
        var storedMessageId = localStorage.getItem(storageKey);
        try {
          storedMessageId.toString();
        }
        catch (error) {
          storedMessageId = "0";
        }

        if (storedMessageId.toString() != dm.message_id.toString() && storedMessageId.toString() != dm.message_id.toString() + "-read") {
          localStorage.setItem(storageKey, dm.message_id);
          if (dm.id.toString() === channelId.toString() && window.location.pathname.includes("dm")) {
            if (!document.hasFocus()) {
              new Notification("New direct message", {body:"New direct message",icon:"https://cdn-icons-png.flaticon.com/512/6405/6405847.png"})
            }
          } else {
            new Notification("New direct message", {body:"New direct message",icon:"https://cdn-icons-png.flaticon.com/512/6405/6405847.png"})
          }
        } else if (!storedMessageId.endsWith('-read')) {
          if (dm.id.toString() === channelId.toString() && window.location.pathname.includes("dm")) {
            document.getElementById(dm.id).style["outline"] = "none";
            localStorage.setItem(storageKey, `${dm.message_id}-read`);
            console.log("Message now read in dm "+dm.id);
          }
          else {
            document.getElementById(dm.id).style["outline"] = "3px solid red";
            console.log("Message still unread in dm "+dm.id)
          }
        }
      }
    })
    .catch((error) => {
      console.error(error);
    })
    .finally(() => {
      setTimeout(() => areThereNewMessagesCheck(channelId), 15000);
    });
}

areThereNewMessagesCheck()

function getNewestMessage() {
  fetch('/channel/'+serverId+'/'+channelId+'/latest.json', {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': '{{ csrf_token }}'
    },
    credentials: 'include'
  })
    .then(response => response.json())
    .then(data => {
        const firstMessageElement = document.querySelector('.chat .message:first-child');
      if (firstMessageElement && firstMessageElement.id == data.id.toString()) {
      } else {
        fetch('/channel/fetch/'+data.id+'/message.json', {
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': '{{ csrf_token }}'
          },
          credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
          if (data.message && data.message.content) {
            const firstMessageElement = document.querySelector('.chat .message:first-child');
            const date = new Date(data.message.timestamp);
            const formatter = new Intl.DateTimeFormat("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
                hour: "numeric",
                minute: "numeric",
                hour12: true,
                timeZone: "UTC",
            });
            
            const parts = formatter.format(date);
            let formattedTime = parts.replaceAll(" at","").replaceAll("AM","a.m.").replaceAll("PM","p.m.").replaceAll(":00","").replace(new Date().getFullYear(), new Date().getFullYear()+",") + " UTC";
            if (firstMessageElement && firstMessageElement.id == data.message.id.toString()) {
            } else {
              const newMessageElement = document.createElement('div');
              newMessageElement.classList.add('message');
              newMessageElement.id = data.message.id;
              if (window.location.pathname.includes("channel")) {
                newMessageElement.innerHTML = `
                  <div class="message-author" id="${data.message.id}">
                    <span class="message-author-name" id="${data.message.author.id}">
                      ${data.message.author.name}
                    </span>
                    <span class="timestamp">
                      ${formattedTime.trim()}
                    </span>
                  </div>
                  <div class="message-content">
                    ${data.message.content}
                    <div class="reactions"><button class="reaction-button" onclick="openEmojiPicker(${data.message.id}, '/channel/${serverId}/${channelId}/update_reaction/${data.message.id}/')">+</button></div>
                  </div>
                `;
              } else {
                newMessageElement.innerHTML = `
                  <div class="message-author" id="${data.message.id}">
                    <span class="message-author-name" id="${data.message.author.id}">
                      ${data.message.author.name}
                    </span>
                    <span class="timestamp">
                      ${formattedTime.trim()}
                    </span>
                  </div>
                  <div class="message-content">
                    ${data.message.content}
                  </div>
                `;
              }
              const chatElement = document.querySelector('.chat');
              chatElement.insertBefore(newMessageElement, chatElement.firstChild);
            }
          }
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {
          
        })
      }
    })
    .catch(error => {
      console.error(error);
    })
    .finally(() => {
      setTimeout(getNewestMessage, 2000);
    });
}

getNewestMessage();

function openEmojiPicker(messageId, link) {
    const emojis = ["💛", "👍", "👎", "👋", "❎", "✅"];
    const existingEmojiPicker = document.querySelector(".emoji-picker");
    if (existingEmojiPicker) {
        return;
    }
    const emojiPicker = document.createElement("div");
    emojiPicker.className = "emoji-picker";
    emojis.forEach((emoji) => {
        const emojiButton = document.createElement("button");
        emojiButton.className = "emoji-button";
        emojiButton.innerText = emoji;
        emojiButton.addEventListener("click", (e) => {
            e.stopPropagation();
            window.open(link + emoji,target="_self");
        });
        emojiPicker.appendChild(emojiButton);
    });
    const messageContainer = document.getElementById(messageId);
    messageContainer.appendChild(emojiPicker);
    document.addEventListener("click", (event) => {
        if (!emojiPicker.contains(event.target) && !event.target.classList.contains("reaction-button")) {
            emojiPicker.remove();
        }
    });
}