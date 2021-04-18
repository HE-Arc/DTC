var alert_infos = [] // Array that have the informations of the alerts currently displayed.

/**
 * Clears all the current alerts.
 * 
 * Is called either because a new one is being fired, or because ones timeout is over.
 */
function clearTimemouts() {

    alert_infos.forEach(time => {

        clearInterval(time.timeout);
        time.message_element.style.display = "none";
    });

    alert_infos = [];
}

/*

NODE ADDED AS ROW :

<li id="user-{{user.id}}" class="list-group-item list-group-item-twitch px-3 py-2">
            <div class="row">
              <div class="col-auto">
                <img class="profile-pic mr-1"
                  src="{{user.pictureURL}}">
                <div class="align-middle d-inline-block font-weight-bold">{{user.username}}</div>
              </div>
              <div class="col v-center justify-content-end">
                <form action="{% url 'unfollow' %}" method="post" class='follow_form'>
                  <p name="output-message" class="mb-0 p-2 font-weight-bold text-uppercase text-twitch-feint bg-success" style="display:none;"></p>
                  <input type="hidden" name="user_id" id="user_id" value="{{user.id}}">
                  <button type="submit" class="btn btn-twitch p-2 lh-0 d-inline-block fs-8">
                    <i class="fas fa-trash"></i>
                  </button>
                </form>
              </div>
    </div>
</li>
*/

function addSubscription(user_id, username, pictureURL) {
    let liNode = document.createElement("li");
    liNode.className = "list-group-item list-group-item-twitch px-3 py-2";
    liNode.id = "user-" + user_id;
    let rowNode = document.createElement("div");
    rowNode.className = "row";
    let colNode = document.createElement("div");
    colNode.className = "col-auto";
    let imgNode = document.createElement("img");
    imgNode.className = "profile-pic mr-1";
    imgNode.src = pictureURL;
    let usernameNode = document.createElement("div");
    usernameNode.className = "align-middle d-inline-block font-weight-bold";
    usernameNode.innerText = username;

    let divButton = document.createElement("div");
    divButton.className = "col v-center justify-content-end";

    let formNode = document.createElement("form");
    formNode.action = url_unfollow;
    formNode.method = 'post';
    formNode.className = 'follow_form';

    formNode.addEventListener("submit", e => onSubmitForm(e, formNode));

    let messageNode = document.createElement("p");
    messageNode.name = "output-message";
    messageNode.className = "mb-0 p-2 font-weight-bold text-uppercase text-twitch-feint bg-success";
    messageNode.style.cssText = "display:none;";

    let inputNode = document.createElement("input");
    inputNode.type = "hidden";
    inputNode.value = user_id;
    inputNode.id = "user_id";
    inputNode.name = "user_id";

    let buttonNode = document.createElement("button");
    buttonNode.type = "submit";
    buttonNode.className = "btn btn-twitch p-2 lh-0 d-inline-block fs-8";

    let iconNode = document.createElement("i");
    iconNode.className = "fas fa-trash";

    liNode.appendChild(rowNode);
    rowNode.appendChild(colNode);
    colNode.appendChild(imgNode);
    colNode.appendChild(usernameNode);

    rowNode.appendChild(divButton);
    divButton.appendChild(formNode);
    formNode.appendChild(messageNode);
    formNode.appendChild(inputNode);
    formNode.appendChild(buttonNode);
    buttonNode.appendChild(iconNode);

    let listSubscriptions = document.getElementById("list-subscriptions");
    listSubscriptions.appendChild(liNode);
}

function deleteSubscription(user_id) {
    let nodeUser = document.getElementById("user-" + user_id);
    nodeUser.remove();

    let nodeLi = document.getElementById("user-search-" + user_id);

    let form = nodeLi.querySelector("form");
    form.action = url_follow;

    let btnNode = nodeLi.querySelector("button")
    btnNode.classList.remove("btn-success");
    btnNode.classList.add("btn-twitch");

    let iconNode = btnNode.querySelector("i");
    iconNode.classList.remove("fa-check");
    iconNode.classList.add("fa-plus");
}


/**
 * Once the content of the DOM is loaded, adds an Event Listener on "submit" to every element with the name "follow_form".
 * 
 * This Event Listener is responsible to like and dislike clips without refreshing the page (fetch API, native JS).
 * Cleans other Timeouts and alerts everytime a like/dislike is emitted so there isn't any visual problems.
 */
document.addEventListener("DOMContentLoaded", function () {

    var follow_forms = document.getElementsByClassName('follow_form');

    for (let follow_form of follow_forms) {
        follow_form.addEventListener("submit", e => onSubmitForm(e, follow_form));
    }
});


function onSubmitForm(e, follow_form) {

    e.preventDefault();

    user_id = follow_form.querySelector('input[name="user_id"]').value;
    //clipURL = follow_form.querySelector('input[name="clipURL"]').value;
    //title_clip = follow_form.querySelector('input[name="title_clip"]').value;
    //thumbnailURL_clip = follow_form.querySelector('input[name="thumbnailURL_clip"]').value;

    const formData = new FormData();

    formData.append('user_id', user_id);
    //formData.append('clipURL', clipURL);
    //formData.append('title_clip', title_clip);
    //formData.append('thumbnailURL_clip', thumbnailURL_clip);
    formData.append('csrfmiddlewaretoken', csrf_token);

    output_message = follow_form.querySelector('p[name="output-message"]');
    btn_like = follow_form.querySelector('button');
    btn_icon = btn_like.querySelector('i')

    chosen_action = follow_form.action;

    fetch(chosen_action, {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {

            if (data.action === 'follow') {
                //output_message.innerText = "Followed !"; //TODO: maybe add username there
                btn_like.classList.remove("btn-twitch");
                btn_like.classList.add("btn-success");
                btn_icon.classList.remove("fa-plus")
                btn_icon.classList.add("fa-check")
                follow_form.action = url_unfollow;

                addSubscription(data.user_id, data.user_name, data.user_picture);

                /*clearTimemouts();

                alert_infos.push({
                    'timeout': setTimeout(function () {
                        clearTimemouts();
                    }, 2500),
                    'message_element': output_message
                });
                alert_infos.push({
                    'timeout': setTimeout(function () {
                        output_message.style.display = "";
                    }, 200),
                    'message_element': output_message
                });*/
            }
            else if (data.action === 'unfollow') {
                //output_message.innerText = "Unfollowed !";  //TODO: maybe add username there
                btn_like.classList.add("btn-twitch");
                btn_like.classList.remove("btn-success");
                btn_icon.classList.add("fa-plus")
                btn_icon.classList.remove("fa-check")
                follow_form.action = url_follow;

                deleteSubscription(data.user_id);
                /*clearTimemouts();

                alert_infos.push({
                    'timeout': setTimeout(function () {
                        clearTimemouts();
                    }, 2500),
                    'message_element': output_message
                });
                alert_infos.push({
                    'timeout': setTimeout(function () {
                        output_message.style.display = "";
                    }, 200),
                    'message_element': output_message
                });*/
            }
        })
        .catch(error => {
            output_message.innerText = "Error. Try again !"

            clearTimemouts();

            alert_infos.push({
                'timeout': setTimeout(function () {
                    output_message.classList.remove("bg-danger");
                    clearTimemouts();
                }, 3200),
                'message_element': output_message
            });
            alert_infos.push({
                'timeout': setTimeout(function () {
                    output_message.style.display = "";
                    output_message.classList.add("bg-danger");
                }, 200),
                'message_element': output_message
            });
        });
}