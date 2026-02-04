function setAppHeight(){
    const vv = window.visualViewport;
    const h = vv ? vv.height : window.innerHeight;
    document.documentElement.style.setProperty("--app-h", `${h}px`);
  }
  
  window.addEventListener("resize", setAppHeight);
  window.addEventListener("orientationchange", setAppHeight);
  
  if(window.visualViewport){
    window.visualViewport.addEventListener("resize", setAppHeight);
    window.visualViewport.addEventListener("scroll", setAppHeight);
  }
  
  setAppHeight();

const ASSETS = {
    intro: "assets/game_Intro.mp4",
    exit: "assets/game_exit.png",
    bgs: [
      "assets/bg_1.png","assets/bg_2.png","assets/bg_3.png",
      "assets/bg_4.png","assets/bg_5.png","assets/bg_6.png",
      "assets/bg_7.png","assets/bg_8.png","assets/bg_9.png"
    ],
    bgm: "assets/bgm.mp3"
  };
  
  const STAGES = ["Easy","Medium","Hard"];
  const QUESTIONS_PER_STAGE = 3;
  const ATTEMPTS_PER_QUESTION = 2;
  const CHOICES_PER_QUESTION = 4;
  
  const MSG_WIN = "Finally you are out. You can exit from the school.";
  const MSG_LOSE = "Game Over";
  
  const app = document.getElementById("app");
  
  function randInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a; }
  function shuffle(arr){
    for(let i=arr.length-1;i>0;i--){
      const j = Math.floor(Math.random()*(i+1));
      [arr[i],arr[j]] = [arr[j],arr[i]];
    }
    return arr;
  }
  
  function uniqueChoices(correct){
    const vals = new Set([correct]);
    while(vals.size < CHOICES_PER_QUESTION){
      const delta = randInt(-8, 8);
      if(delta === 0) continue;
      const cand = correct + delta;
      if(cand < 0) continue;
      vals.add(cand);
    }
    return shuffle(Array.from(vals));
  }
  
  function buildQuestion(stage, prompt, correct){
    return {
      stage,
      prompt,
      correct,
      choices: uniqueChoices(correct),
      attemptsLeft: ATTEMPTS_PER_QUESTION
    };
  }
  
  function makeEasy(){
    let a = randInt(1,20);
    let b = randInt(1,20);
    const add = randInt(0,1) === 0;
    if(!add && b > a){ const t=a; a=b; b=t; }
    const correct = add ? a+b : a-b;
    const prompt = add ? `${a} + ${b} = ?` : `${a} - ${b} = ?`;
    return buildQuestion("Easy", prompt, correct);
  }
  
  function makeMedium(){
    const mult = randInt(0,1) === 0;
    if(mult){
      const a = randInt(2,12);
      const b = randInt(2,12);
      return buildQuestion("Medium", `${a} × ${b} = ?`, a*b);
    }
    const d = randInt(2,12);
    const q = randInt(2,12);
    const dividend = d*q;
    return buildQuestion("Medium", `${dividend} ÷ ${d} = ?`, q);
  }
  
  function makeHard(){
    const t = randInt(1,3);
    if(t === 1){
      const c = randInt(2,9);
      const val = randInt(30,120);
      const target = val - (val % c);
      const a = randInt(5, Math.max(6, target - 5));
      const b = target - a;
      return buildQuestion("Hard", `(${a} + ${b}) ÷ ${c} = ?`, Math.floor(target / c));
    }
    if(t === 2){
      const a = randInt(5,16);
      const b = randInt(10,28);
      let c = randInt(2,10);
      if(c >= b) c = 2;
      return buildQuestion("Hard", `${a} × (${b} - ${c}) = ?`, a*(b-c));
    }
    const x = randInt(5,50);
    const y = randInt(2,12);
    const z = randInt(2,12);
    return buildQuestion("Hard", `${x} + ${y} × ${z} = ?`, x + (y*z));
  }
  
  function nextQuestion(stage){
    if(stage === "Easy") return makeEasy();
    if(stage === "Medium") return makeMedium();
    return makeHard();
  }
  
  const state = {
    screen: "intro",
    stageIndex: 0,
    solved: 0,
    question: null,
    questionIndex: 0,
    toastText: "",
    toastColor: "",
    toastUntil: 0
  };

  const audioState = {
    started: false,
    audio: null
    };
    
  function initBgm(){
        if(audioState.audio) return;
            const a = new Audio(ASSETS.bgm);
            a.preload = "auto";
            a.loop = true;
            a.volume = 0.6;
            a.addEventListener("ended", () => {
            a.currentTime = 0;
            a.play().catch(() => {});
            });
            audioState.audio = a;
  }
    
  function startBgm(){
        initBgm();
        if(audioState.started) return;
            audioState.started = true;
            audioState.audio.play().catch(() => {});
  }
    
  function pauseBgm(){
        if(!audioState.audio) return;
            audioState.audio.pause();
  }
    
  function resumeBgm(){
        if(!audioState.audio) return;
        if(!audioState.started) return;
        audioState.audio.play().catch(() => {});
  }
  function ensureBgm(){
    if(!audioState.started) return;
    if(!audioState.audio) return;
    audioState.audio.play().catch(()=>{});
  }
  function setToast(text, color, ms){
    state.toastText = text;
    state.toastColor = color;
    state.toastUntil = Date.now() + ms;
  }
  
  function clearToastIfNeeded(){
    if(state.toastText && Date.now() > state.toastUntil){
      state.toastText = "";
    }
  }
  
  function resetGame(){
    pauseBgm();
    state.screen = "intro";
    state.stageIndex = 0;
    state.solved = 0;
    state.question = null;
    state.questionIndex = 0;
    state.toastText = "";
    state.toastColor = "";
    state.toastUntil = 0;
  }
  
  function bgForQuestion(){
    const idx = (state.questionIndex - 1) % ASSETS.bgs.length;
    return ASSETS.bgs[Math.max(0, idx)];
  }
  window.addEventListener("pagehide", () => {
    pauseBgm();
    });
    
    document.addEventListener("visibilitychange", () => {
    if(document.hidden) pauseBgm();
    else resumeBgm();
    });

  function render(){
    clearToastIfNeeded();
    if(state.screen === "intro") return renderIntro();
    if(state.screen === "instructions") return renderInstructions();
    if(state.screen === "hub") return renderHub();
    if(state.screen === "question") return renderQuestion();
    if(state.screen === "win") return renderWin();
    return renderLose();
  }
  
  function renderIntro(){
    app.innerHTML = `
      <div class="screen" id="introRoot">
        <div class="videoWrap">
          <video id="introVid"
                 playsinline
                 autoplay
                 preload="auto"
                 src="${ASSETS.intro}">
          </video>
        </div>
  
        <div class="videoControls">
          <button class="btn" id="skipIntro">Skip</button>
        </div>
      </div>
    `;
  
    const root = document.getElementById("introRoot");
    const vid = document.getElementById("introVid");
    const skip = document.getElementById("skipIntro");
  
    // Start muted to satisfy iOS autoplay
    vid.muted = true;
  
    function unlockAudio(){
      startBgm();        // background music
      vid.muted = false; // enable video sound
      vid.play().catch(()=>{});
    }
    

    // One tap anywhere unlocks audio
    root.addEventListener("pointerdown", unlockAudio, { once:true });
    vid.addEventListener("pointerdown", unlockAudio, { once:true });
  
    skip.addEventListener("click", () => {
      unlockAudio();
      state.screen = "instructions";
      render();
    });
  
    vid.addEventListener("ended", () => {
      state.screen = "instructions";
      render();
    });
  
    vid.play().catch(()=>{});
  }
  
  function renderInstructions(){
    ensureBgm();
    app.innerHTML = `
      <div class="screen">
        <div class="center">
          <div class="card">
            <div class="title" style="font-size:34px">Instructions</div>
            <div class="subtitle" style="margin-top:12px; text-align:left">
              1. Escape three rooms. Easy, Medium, Hard.<br>
              2. Each room has three math questions.<br>
              3. Each question has two attempts.<br>
              4. Answers are multiple choice.<br>
              5. Three correct answers unlock next room.<br>
              6. Finish Hard room to exit the school.
            </div>
          </div>
          <div class="btnrow">
            <button class="btn primary" id="startGame">Start</button>
          </div>
        </div>
      </div>
    `;
    document.getElementById("startGame").addEventListener("click", () => {
      startBgm();
      state.screen = "hub";
      render();
    });
  }
  
  function renderHub(){
    ensureBgm();
    const stage = STAGES[state.stageIndex];
    app.innerHTML = `
      <div class="screen">
        <div class="center">
          <div class="card">
            <div class="title" style="font-size:34px">Room</div>
            <div class="subtitle" style="margin-top:10px; text-align:left">
              Stage: ${stage}<br>
              Solved: ${state.solved}/${QUESTIONS_PER_STAGE}<br>
              Goal: solve three questions to escape this room
            </div>
          </div>
          <div class="btnrow">
            <button class="btn primary" id="startRoom">Start room</button>
          </div>
        </div>
      </div>
    `;
    document.getElementById("startRoom").addEventListener("click", () => {
      startBgm();
      const stageNow = STAGES[state.stageIndex];
      state.question = nextQuestion(stageNow);
      state.questionIndex += 1;
      state.screen = "question";
      render();
    });
  }
  
  function renderQuestion(){
    ensureBgm();
    const stage = STAGES[state.stageIndex];
  
    if(!state.question){
      state.question = nextQuestion(stage);
      state.questionIndex += 1;
    }
  
    const bgUrl = bgForQuestion();
  
    app.innerHTML = `
      <div class="screen">
        <div class="bg" style="background-image:url('${bgUrl}')"></div>
        <div class="overlay"></div>
  
        <div class="topbar">
          <div>Stage: ${stage} &nbsp;&nbsp; Solved: ${state.solved}/${QUESTIONS_PER_STAGE}</div>
          <div>Attempts left: ${state.question.attemptsLeft}</div>
        </div>
  
        <div class="qwrap">
          <div class="qcard">
            <div class="qhint">Solve to escape</div>
            <div class="qtext">${state.question.prompt}</div>
          </div>
        </div>
  
        <div class="choices" id="choices"></div>
  
        ${state.toastText ? `<div class="toast"><span style="color:${state.toastColor}">${state.toastText}</span></div>` : ``}
      </div>
    `;
  
    const choicesDiv = document.getElementById("choices");
  
    choicesDiv.innerHTML = state.question.choices.map((c, i) => {
      return `<button class="choice" type="button" data-i="${i}">${c}</button>`;
    }).join("");
  
    choicesDiv.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.currentTarget.blur();
          onChoose(Number(btn.getAttribute("data-i")));
        });
      });
  }
  
  function onChoose(i){
    const q = state.question;
    const chosen = q.choices[i];
  
    if(chosen === q.correct){
      setToast("Correct", "var(--ok)", 700);
      state.solved += 1;
  
      if(state.solved >= QUESTIONS_PER_STAGE){
        state.stageIndex += 1;
        state.solved = 0;
        state.question = null;
  
        if(state.stageIndex >= STAGES.length){
          state.screen = "win";
        }else{
          state.screen = "hub";
        }
        render();
        return;
      }
  
      const stageNow = STAGES[state.stageIndex];
      state.question = nextQuestion(stageNow);
      state.questionIndex += 1;
      render();
      return;
    }
  
    q.attemptsLeft -= 1;
    if(q.attemptsLeft > 0){
      setToast("Wrong. Try again", "var(--bad)", 900);
      render();
      return;
    }
  
    state.screen = "lose";
    render();
  }
  
  function renderWin(){
    ensureBgm();
    app.innerHTML = `
      <div class="screen">
        <div class="bg" style="background-image:url('${ASSETS.exit}')"></div>
        <div class="overlay"></div>
        <div class="center">
          <div class="card">
            <div class="title" style="font-size:34px">Escaped</div>
            <div class="subtitle" style="margin-top:12px">${MSG_WIN}</div>
          </div>
          <div class="btnrow">
            <button class="btn primary" id="againWin">Start again</button>
          </div>
        </div>
      </div>
    `;
    document.getElementById("againWin").addEventListener("click", () => {
      resetGame();
      render();
    });
  }
  
  function renderLose(){
    ensureBgm();
    app.innerHTML = `
      <div class="screen">
        <div class="center">
          <div class="card">
            <div class="title" style="font-size:34px; color:var(--bad)">${MSG_LOSE}</div>
            <div class="subtitle" style="margin-top:12px">
              You used all attempts on a question.
            </div>
          </div>
          <div class="btnrow">
            <button class="btn primary" id="againLose">Start again</button>
          </div>
        </div>
      </div>
    `;
    document.getElementById("againLose").addEventListener("click", () => {
      resetGame();
      render();
    });
  }
  
  if("serviceWorker" in navigator){
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("sw.js").catch(() => {});
    });
  }
  
  render();