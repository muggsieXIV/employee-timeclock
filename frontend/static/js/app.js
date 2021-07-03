const clock = document.querySelector('.clock');

const time = () => {
    const now = new Date();

    const date = dateFns.format(now, 'dddd Do MMMM YYYY');
    const hours = dateFns.format(now, 'hh');
    const minutes = dateFns.format(now, 'mm');
    const seconds = dateFns.format(now, 'ss');

    const html = `
    <div>${date}</div>
    <div class="time">
        <span>${hours}</span> :
        <span>${minutes}</span> :
        <span>${seconds}</span>
    </div>
    `;

    clock.innerHTML = html;

};

setInterval(time, 1000);