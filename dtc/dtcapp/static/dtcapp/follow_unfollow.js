/**
 * Once the content of the DOM is loaded, adds an Event Listener on "submit" to every element with the name "follow_form".
 * 
 * This Event Listener is responsible to like and dislike clips without refreshing the page (fetch API, native JS).
 * Cleans other Timeouts and alerts everytime a like/dislike is emitted so there isn't any visual problems.
 */
 document.addEventListener("DOMContentLoaded", function () {

    var follow_forms = document.getElementsByClassName('follow_form');

    for (let follow_form of follow_forms) {

        follow_form.addEventListener("submit", function (e) {

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
            btn_like = follow_form.querySelector('input[name="btn_like"]');

            chosen_action = follow_form.action;

            fetch(chosen_action, {
                method: "POST",
                body: formData
            })
                .then(response => response.json())
                .then(data => {

                    if (data.action === 'like') {
                        output_message.innerText = "The clip has been added to your liked list !";
                        btn_like.classList.remove("btn-twitch-reversed");
                        btn_like.classList.add("btn-twitch");
                        follow_form.action = url_dislike;

                        clearTimemouts();

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
                        });
                    }
                    else if (data.action === 'dislike') {
                        output_message.innerText = "The clip has been removed from your liked list !";
                        btn_like.classList.remove("btn-twitch");
                        btn_like.classList.add("btn-twitch-reversed");
                        follow_form.action = url_like;

                        clearTimemouts();

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
                        });
                    }
                })
                .catch(error => {
                    output_message.innerText = "There has been a problem ! Retry again later."

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
        });

    }
});