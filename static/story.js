const player = document.getElementById("player");

function fill_container(container, language) {
  language.forEach((line) => {
    const elt = document.createElement('li');
    elt.innerHTML = `${line.character}: ${line.line}`;
    elt.setAttribute('data-start', line.start_sec);
    elt.setAttribute('data-end', line.end_sec);
    elt.setAttribute('class', 'list-group-item')
    elt.addEventListener('click', () => {
        if (!player.paused && player.currentTime >= line.start_sec && player.currentTime < line.end_sec) {
            player.pause();
        } else {
            player.currentTime = line.start_sec;
            player.play();
        }
    });
    container.appendChild(elt);
  });
}

const foreign_language = document.getElementById('foreign');
const english = document.getElementById('english');
fill_container(foreign_language, story.story.foreign_language);
fill_container(english, story.story.english);

player.addEventListener('timeupdate', () => {
    const time = player.currentTime;
    const foreign = document.getElementById('foreign');
    const english = document.getElementById('english');
    const foreign_lines = foreign.querySelectorAll('li');
    const english_lines = english.querySelectorAll('li');
    
    foreign_lines.forEach((line, index) => {
        const start = parseFloat(line.getAttribute('data-start'));
        const end = parseFloat(line.getAttribute('data-end'));
        if (time >= start && time < end) {
            line.classList.add('active');
            english_lines[index].classList.add('active');
        } else {
            line.classList.remove('active');
            english_lines[index].classList.remove("active");

            // line.style.color = 'black';
            // english_lines[index].style.color = 'black';
        }
    });
});