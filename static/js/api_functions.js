function call_mining() {
  const body_to_fade = document.getElementById("all_stuff");
  body_to_fade.style.opacity = "0.35";

  const spinner = document.getElementById("spinner");
  spinner.removeAttribute("hidden");

  setTimeout(function() {
    fetch("/mine_block", {
      method: "POST"
    }).then(response => {
      spinner.setAttribute("hidden", "");
      document.location.reload(true);
    });
  }, 500);
}

function call_consensus() {
  const body_to_fade = document.getElementById("all_stuff");
  body_to_fade.style.opacity = "0.35";

  const spinner = document.getElementById("spinner");
  spinner.removeAttribute("hidden");
  setTimeout(function() {
    fetch("/consensus", {
      method: "POST"
    }).then(response => {
      spinner.setAttribute("hidden", "");

      document.location.reload(true);
    });
  }, 500);
}

function add_peer() {
  var headers = {
    "Content-Type": "application/json"
  };

  const inputs = document.getElementById("add_peer_form").elements;
  const node_url_val = inputs.node_url.value;

  fetch("/node", {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: headers,
    body: JSON.stringify({ node_url: node_url_val })
  }).then(response => {
    document.location.reload(true);
  });
}

function send_tx() {
  var headers = {
    "Content-Type": "application/json"
  };

  const inputs = document.getElementById("add_tx_form").elements;
  const receiver_val = inputs.receiver.value;
  const amount_val = inputs.amount.value;

  fetch("/transaction", {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: headers,
    body: JSON.stringify({ receiver: receiver_val, amount: amount_val })
  }).then(response => {
    document.location.reload(true);
  });
}
