// ===============================
// DASHBOARD FUNCTIONS
// ===============================
function selectSection(section) {
  // Hide all form sections first
  document.querySelectorAll('.form-section').forEach(form => {
    form.classList.remove('active');
  });
  
  // Hide section cards
  document.querySelectorAll('.section-card').forEach(card => {
    card.style.display = 'none';
  });
  
  // Show selected form section
  if (section === 'tenth') {
    document.getElementById('tenthForm').classList.add('active');
  } else if (section === 'twelfth') {
    document.getElementById('twelfthForm').classList.add('active');
  }
}

function goBack() {
  // Show all section cards
  document.querySelectorAll('.section-card').forEach(card => {
    card.style.display = 'block';
  });
  
  // Hide all form sections
  document.querySelectorAll('.form-section').forEach(form => {
    form.classList.remove('active');
  });
  
  // Clear results
  document.getElementById('tenthResult').innerHTML = '';
  document.getElementById('tenthAnalysis').innerHTML = '';
  document.getElementById('twelfthResult').innerHTML = '';
  document.getElementById('twelfthAnalysis').innerHTML = '';
}

// ===============================
// AUTHENTICATION FUNCTIONS
// ===============================
async function login() {
  const email = document.getElementById("loginEmail")?.value.trim();
  const password = document.getElementById("loginPassword")?.value.trim();

  if (!email || !password) {
    alert("Please fill in both fields.");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    console.log("Login Response:", data);

    if (response.ok && data.status === "success") {
      alert(`Welcome, ${data.user.name}!`);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "./index.html";
    } else {
      alert(data.message || "Login failed.");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Server error. Please ensure Flask backend is running on port 5000.");
  }
}

async function signup() {
  const name = document.getElementById("signupName")?.value.trim();
  const email = document.getElementById("signupEmail")?.value.trim();
  const password = document.getElementById("signupPassword")?.value.trim();

  if (!name || !email || !password) {
    alert("Please fill all fields.");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });

    const data = await response.json();
    console.log("Signup Response:", data);

    if (response.ok && data.status === "success") {
      alert("Signup successful! Redirecting to login...");
      window.location.href = "login.html";
    } else {
      alert(data.message || "Signup failed.");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Server error. Please ensure Flask backend is running.");
  }
}

// ===============================
// 10TH STANDARD ANALYSIS FUNCTION
// ===============================
async function analyzeTenthStrengths() {
  const progressContainer = document.getElementById('tenthProgressContainer');
  const progressBar = document.getElementById('tenthProgressBar');
  const resultElement = document.getElementById('tenthResult');
  const analysisElement = document.getElementById('tenthAnalysis');
  
  // Show loading state
  progressContainer.classList.add('show');
  progressBar.style.width = '0%';
  resultElement.innerHTML = '';
  analysisElement.innerHTML = '';

  // Get input values
  const science = parseFloat(document.getElementById('tenth_science').value);
  const english = parseFloat(document.getElementById('tenth_english').value);
  const maths = parseFloat(document.getElementById('tenth_maths').value);
  
  // Get psychometric scores
  const analytical_thinking = parseInt(document.getElementById('tenth_analytical_thinking').value);
  const creativity = parseInt(document.getElementById('tenth_creativity').value);
  const leadership = parseInt(document.getElementById('tenth_leadership').value);
  const problem_solving = parseInt(document.getElementById('tenth_problem_solving').value);
  const communication = parseInt(document.getElementById('tenth_communication').value);
  
  // Get interests
  const interest1 = document.getElementById('tenth_interest1').value;
  const interest2 = document.getElementById('tenth_interest2').value;
  const interest3 = document.getElementById('tenth_interest3').value;

  // Validate academic marks
  if (isNaN(science) || isNaN(english) || isNaN(maths)) {
    alert("⚠️ Please fill all marks fields with valid numbers!");
    progressContainer.classList.remove('show');
    return;
  }

  if (science < 0 || science > 100 || english < 0 || english > 100 || maths < 0 || maths > 100) {
    alert("⚠️ All marks must be between 0 and 100!");
    return;
  }

  // Validate psychometric scores
  if (isNaN(analytical_thinking) || isNaN(creativity) || isNaN(leadership) || 
      isNaN(problem_solving) || isNaN(communication)) {
    alert("⚠️ Please rate all psychometric questions (1-5)!");
    return;
  }

  if (!interest1 || !interest2) {
    alert("⚠️ Please select at least two required interests!");
    return;
  }

  // Animate progress bar
  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    progressBar.style.width = `${progress}%`;
    if (progress >= 90) {
      clearInterval(interval);
    }
  }, 200);

  const payload = {
    standard: "10th",
    science,
    english,
    maths,
    analytical_thinking,
    creativity,
    leadership,
    problem_solving,
    communication,
    interest1,
    interest2,
    interest3: interest3 || ""
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    clearInterval(interval);
    progressBar.style.width = '100%';

    const data = await response.json();
    if (data.error) {
      resultElement.innerHTML = `<div class="error-message">❌ <strong>Error:</strong> ${data.error}</div>`;
    } else {
      resultElement.innerHTML = `<div class="success-message">✅ <strong>Personalized Analysis Complete!</strong> Discovered ${data.career_recommendations.length} career paths that match your unique profile.</div>`;
      displayAnalysisResults(data, analysisElement, "10th");
    }
    
    // Hide progress bar after delay
    setTimeout(() => {
      progressContainer.classList.remove('show');
    }, 1000);

  } catch (err) {
    console.error(err);
    clearInterval(interval);
    progressContainer.classList.remove('show');
    
    resultElement.innerHTML = `<div class="error-message">❌ <strong>Server Error:</strong> Could not connect to analysis service. Please try again later.</div>`;
  }
}

// ===============================
// 12TH STANDARD ANALYSIS FUNCTION
// ===============================
async function analyzeTwelfthStrengths() {
  const progressContainer = document.getElementById('twelfthProgressContainer');
  const progressBar = document.getElementById('twelfthProgressBar');
  const resultElement = document.getElementById('twelfthResult');
  const analysisElement = document.getElementById('twelfthAnalysis');
  
  // Show loading state
  progressContainer.classList.add('show');
  progressBar.style.width = '0%';
  resultElement.innerHTML = '';
  analysisElement.innerHTML = '';

  // Get input values
  const physics = parseFloat(document.getElementById('twelfth_physics').value);
  const chemistry = parseFloat(document.getElementById('twelfth_chemistry').value);
  const maths = parseFloat(document.getElementById('twelfth_maths').value);
  const biology = parseFloat(document.getElementById('twelfth_biology').value);
  
  // Get psychometric scores
  const analytical_thinking = parseInt(document.getElementById('twelfth_analytical_thinking').value);
  const creativity = parseInt(document.getElementById('twelfth_creativity').value);
  const leadership = parseInt(document.getElementById('twelfth_leadership').value);
  const problem_solving = parseInt(document.getElementById('twelfth_problem_solving').value);
  const communication = parseInt(document.getElementById('twelfth_communication').value);
  
  // Get interests
  const interest1 = document.getElementById('twelfth_interest1').value;
  const interest2 = document.getElementById('twelfth_interest2').value;
  const interest3 = document.getElementById('twelfth_interest3').value;

  // Validate academic marks
  if (isNaN(physics) || isNaN(chemistry) || isNaN(maths) || isNaN(biology)) {
    alert("⚠️ Please fill all marks fields with valid numbers!");
    progressContainer.classList.remove('show');
    return;
  }

  if (physics < 0 || physics > 100 || chemistry < 0 || chemistry > 100 || 
      maths < 0 || maths > 100 || biology < 0 || biology > 100) {
    alert("⚠️ All marks must be between 0 and 100!");
    return;
  }

  // Validate psychometric scores
  if (isNaN(analytical_thinking) || isNaN(creativity) || isNaN(leadership) || 
      isNaN(problem_solving) || isNaN(communication)) {
    alert("⚠️ Please rate all psychometric questions (1-5)!");
    return;
  }

  if (!interest1 || !interest2) {
    alert("⚠️ Please select at least two required interests!");
    return;
  }

  // Animate progress bar
  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    progressBar.style.width = `${progress}%`;
    if (progress >= 90) {
      clearInterval(interval);
    }
  }, 200);

  const payload = {
    standard: "12th",
    physics,
    chemistry,
    maths,
    biology,
    analytical_thinking,
    creativity,
    leadership,
    problem_solving,
    communication,
    interest1,
    interest2,
    interest3: interest3 || ""
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    clearInterval(interval);
    progressBar.style.width = '100%';

    const data = await response.json();
    if (data.error) {
      resultElement.innerHTML = `<div class="error-message">❌ <strong>Error:</strong> ${data.error}</div>`;
    } else {
      resultElement.innerHTML = `<div class="success-message">✅ <strong>Personalized Analysis Complete!</strong> Discovered ${data.career_recommendations.length} career paths that match your unique profile.</div>`;
      displayAnalysisResults(data, analysisElement, "12th");
    }
    
    // Hide progress bar after delay
    setTimeout(() => {
      progressContainer.classList.remove('show');
    }, 1000);

  } catch (err) {
    console.error(err);
    clearInterval(interval);
    progressContainer.classList.remove('show');
    
    resultElement.innerHTML = `<div class="error-message">❌ <strong>Server Error:</strong> Could not connect to analysis service. Please try again later.</div>`;
  }
}

// ===============================
// DISPLAY ANALYSIS RESULTS (Updated - Without Timeline)
// ===============================
function displayAnalysisResults(data, analysisElement, standard) {
  let analysisHTML = `<div class="analysis-container">
    <h3>🎯 Your 100% Personalized Career Analysis</h3>
    <p class="analysis-subtitle">Customized specifically for YOUR scores, personality, and interests</p>`;
  
  // Profile Summary with exact scores
  if (data.profile_summary) {
    analysisHTML += `
      <div class="profile-summary">
        <h4>📋 Your Unique Profile Snapshot</h4>
        <p>${data.profile_summary}</p>
      </div>`;
  }
  
  // Academic Analysis with exact percentages
  if (data.strength_analysis.academic_profile) {
    analysisHTML += `
      <div class="academic-profile">
        <h4>📊 Your Academic Analysis</h4>
        <p><strong>Overall Performance:</strong> ${data.strength_analysis.academic_profile}</p>`;
    
    // Show exact scores with color coding
    if (data.strength_analysis.strong_subjects && data.strength_analysis.strong_subjects.length > 0) {
      analysisHTML += `<div class="score-section">
        <h5>🏆 Your Strengths (80%+)</h5>
        <div class="score-badges">`;
      
      data.strength_analysis.strong_subjects.forEach(subject => {
        analysisHTML += `<span class="score-badge excellent">${subject}: 85%+</span>`;
      });
      
      analysisHTML += `</div></div>`;
    }
    
    if (data.strength_analysis.average_subjects && data.strength_analysis.average_subjects.length > 0) {
      analysisHTML += `<div class="score-section">
        <h5>📈 Average Performance (60-79%)</h5>
        <div class="score-badges">`;
      
      data.strength_analysis.average_subjects.forEach(subject => {
        analysisHTML += `<span class="score-badge average">${subject}: 65%+</span>`;
      });
      
      analysisHTML += `</div></div>`;
    }
    
    if (data.strength_analysis.weak_subjects && data.strength_analysis.weak_subjects.length > 0) {
      analysisHTML += `<div class="score-section">
        <h5>📝 Needs Improvement (<60%)</h5>
        <div class="score-badges">`;
      
      data.strength_analysis.weak_subjects.forEach(subject => {
        analysisHTML += `<span class="score-badge weak">${subject}: <60%</span>`;
      });
      
      analysisHTML += `</div></div>`;
    }
    
    analysisHTML += `</div>`;
  }
  
  // Psychometric Analysis with exact scores
  if (data.strength_analysis.psychometric_profile) {
    analysisHTML += `
      <div class="psychometric-profile">
        <h4>💪 Your Personality Analysis</h4>
        <p><strong>Overall Profile:</strong> ${data.strength_analysis.psychometric_profile}</p>`;
    
    if (data.strength_analysis.psychometric_strengths && data.strength_analysis.psychometric_strengths.length > 0) {
      analysisHTML += `<div class="trait-section">
        <h5>✨ Your Strengths (4-5/5)</h5>
        <div class="trait-badges">`;
      
      data.strength_analysis.psychometric_strengths.forEach(trait => {
        analysisHTML += `<span class="trait-badge strong">${trait}: 4-5/5</span>`;
      });
      
      analysisHTML += `</div></div>`;
    }
    
    if (data.strength_analysis.psychometric_weaknesses && data.strength_analysis.psychometric_weaknesses.length > 0) {
      analysisHTML += `<div class="trait-section">
        <h5>🎯 Areas to Develop (1-2/5)</h5>
        <div class="trait-badges">`;
      
      data.strength_analysis.psychometric_weaknesses.forEach(trait => {
        analysisHTML += `<span class="trait-badge weak">${trait}: 1-2/5</span>`;
      });
      
      analysisHTML += `</div></div>`;
    }
    
    analysisHTML += `</div>`;
  }
  
  // Interests with personalized implications
  if (data.strength_analysis.user_interests && data.strength_analysis.user_interests.length > 0) {
    analysisHTML += `
      <div class="interests-section">
        <h4>❤️ Your Key Interests & Implications</h4>
        <div class="interest-grid">`;
    
    data.strength_analysis.user_interests.forEach(interest => {
      let implication = "";
      let icon = "⭐";
      
      if (interest.toLowerCase().includes('tech') || interest.toLowerCase().includes('computer')) {
        implication = "Leads to IT/Software careers";
        icon = "💻";
      } else if (interest.toLowerCase().includes('medic') || interest.toLowerCase().includes('health')) {
        implication = "Points to Healthcare fields";
        icon = "🏥";
      } else if (interest.toLowerCase().includes('engineer')) {
        implication = "Suggests Engineering paths";
        icon = "⚙️";
      } else if (interest.toLowerCase().includes('busi') || interest.toLowerCase().includes('financ')) {
        implication = "Indicates Commerce/Management";
        icon = "💼";
      } else if (interest.toLowerCase().includes('art') || interest.toLowerCase().includes('creativ')) {
        implication = "Points to Creative careers";
        icon = "🎨";
      } else if (interest.toLowerCase().includes('research')) {
        implication = "Suggests Academic/R&D";
        icon = "🔬";
      } else if (interest.toLowerCase().includes('writ')) {
        implication = "Indicates Communication fields";
        icon = "✍️";
      } else {
        implication = "Explore related career options";
        icon = "🔍";
      }
      
      analysisHTML += `
        <div class="interest-card">
          <span class="interest-icon">${icon}</span>
          <span class="interest-name">${interest}</span>
          <span class="interest-implication">${implication}</span>
        </div>`;
    });
    
    analysisHTML += `</div></div>`;
  }
  
  // Top Career Matches with personalized scores
  analysisHTML += `
    <div class="career-recommendations">
      <h4>🚀 Top Career Matches for YOUR Profile</h4>
      <p class="recommendation-intro">These careers match YOUR specific combination of scores, personality, and interests:</p>`;
  
  data.career_recommendations.forEach((career, index) => {
    let matchLevel = "";
    let matchColor = "";
    
    if (career.match_score >= 8) {
      matchLevel = "Excellent Match";
      matchColor = "excellent-match";
    } else if (career.match_score >= 6) {
      matchLevel = "Good Match";
      matchColor = "good-match";
    } else {
      matchLevel = "Potential Match";
      matchColor = "potential-match";
    }
    
    analysisHTML += `
      <div class="career-card ${index === 0 ? 'top-career' : ''} ${matchColor}">
        <div class="career-header">
          <h5>${index + 1}. ${career.career}</h5>
          <div class="match-info">
            <span class="match-score">Match: ${career.match_score.toFixed(1)}/10</span>
            <span class="match-level">${matchLevel}</span>
          </div>
        </div>
        <p class="career-reason">${career.reason}</p>`;
    
    if (career.required_skills && career.required_skills.length > 0) {
      analysisHTML += `<div class="required-skills">
          <h6>💡 Skills YOU Need:</h6>
          <div class="skill-tags">`;
      
      career.required_skills.forEach(skill => {
        analysisHTML += `<span class="skill-tag">${skill}</span>`;
      });
      
      analysisHTML += `</div></div>`;
    }
    
    analysisHTML += `</div>`;
  });
  
  analysisHTML += `</div>`;
  
  // PERSONALIZED ACTION PLAN (Without timeline)
  if (data.recommended_actions && data.recommended_actions.length > 0) {
    analysisHTML += `
      <div class="personalized-actions">
        <h4>🎯 Your 100% Personalized Action Plan</h4>
        <p class="actions-intro">Customized actions based on YOUR exact scores and profile:</p>
        
        <div class="action-categories">`;
    
    // Categorize actions
    const urgentActions = [];
    const academicActions = [];
    const personalityActions = [];
    const interestActions = [];
    const standardActions = [];
    
    data.recommended_actions.forEach(action => {
      if (action.includes('🚨') || action.includes('⚠️') || action.includes('CRITICAL')) {
        urgentActions.push(action);
      } else if (action.includes('%') || action.includes('subject') || action.includes('Subject')) {
        academicActions.push(action);
      } else if (action.includes('/5') || action.includes('trait') || action.includes('Trait')) {
        personalityActions.push(action);
      } else if (action.includes('interest') || action.includes('Interest')) {
        interestActions.push(action);
      } else if (action.includes('10th') || action.includes('12th')) {
        standardActions.push(action);
      } else {
        urgentActions.push(action); // Default to urgent
      }
    });
    
    // Urgent Actions (if any)
    if (urgentActions.length > 0) {
      analysisHTML += `
        <div class="action-category urgent">
          <h5>🚨 Urgent Actions </h5>
          <ul>`;
      
      urgentActions.forEach((action, idx) => {
        analysisHTML += `<li class="urgent-action">
          <span class="action-number">${idx + 1}</span>
          <span class="action-text">${action}</span>
        </li>`;
      });
      
      analysisHTML += `</ul></div>`;
    }
    
    // Academic Actions
    if (academicActions.length > 0) {
      analysisHTML += `
        <div class="action-category academic">
          <h5>📚 Academic Improvement Plan</h5>
          <ul>`;
      
      academicActions.forEach((action, idx) => {
        analysisHTML += `<li class="academic-action">
          <span class="action-icon">📖</span>
          <span class="action-text">${action}</span>
        </li>`;
      });
      
      analysisHTML += `</ul></div>`;
    }
    
    // Personality Development
    if (personalityActions.length > 0) {
      analysisHTML += `
        <div class="action-category personality">
          <h5>💪 Personality Development</h5>
          <ul>`;
      
      personalityActions.forEach((action, idx) => {
        analysisHTML += `<li class="personality-action">
          <span class="action-icon">🌟</span>
          <span class="action-text">${action}</span>
        </li>`;
      });
      
      analysisHTML += `</ul></div>`;
    }
    
    // Interest Development
    if (interestActions.length > 0) {
      analysisHTML += `
        <div class="action-category interest">
          <h5>❤️ Interest Development</h5>
          <ul>`;
      
      interestActions.forEach((action, idx) => {
        analysisHTML += `<li class="interest-action">
          <span class="action-icon">🎯</span>
          <span class="action-text">${action}</span>
        </li>`;
      });
      
      analysisHTML += `</ul></div>`;
    }
    
    // Standard-specific Actions
    if (standardActions.length > 0) {
      analysisHTML += `
        <div class="action-category standard">
          <h5>${standard === "10th" ? "🔬 10th Standard Focus" : "🎓 12th Standard Focus"}</h5>
          <ul>`;
      
      standardActions.forEach((action, idx) => {
        analysisHTML += `<li class="standard-action">
          <span class="action-icon">${standard === "10th" ? "🎯" : "🚀"}</span>
          <span class="action-text">${action}</span>
        </li>`;
      });
      
      analysisHTML += `</ul></div>`;
    }
    
    analysisHTML += `</div>`;
  }
  
  // Personalized Suggestions
  if (data.personalized_suggestions && data.personalized_suggestions.length > 0) {
    analysisHTML += `
      <div class="personalized-suggestions">
        <h4>💡 Career Insights for YOU</h4>
        <div class="suggestion-grid">`;
    
    data.personalized_suggestions.forEach((suggestion, index) => {
      let category = "general";
      if (suggestion.includes("SCIENCE") || suggestion.includes("Engineering") || suggestion.includes("Medical")) category = "science";
      else if (suggestion.includes("COMMERCE") || suggestion.includes("Business")) category = "commerce";
      else if (suggestion.includes("ARTS") || suggestion.includes("Creative")) category = "arts";
      else if (suggestion.includes("Tech") || suggestion.includes("Computer")) category = "tech";
      
      analysisHTML += `
        <div class="suggestion-card ${category}">
          <span class="suggestion-number">${index + 1}</span>
          <p class="suggestion-text">${suggestion}</p>
        </div>`;
    });
    
    analysisHTML += `</div></div>`;
  }
  
  // Career Insights
  if (data.career_insights && data.career_insights.length > 0) {
    analysisHTML += `
      <div class="career-insights">
        <h4>🔍 Strategic Insights for YOUR Future</h4>
        <ul>`;
    
    data.career_insights.forEach(insight => {
      analysisHTML += `<li>✨ ${insight}</li>`;
    });
    
    analysisHTML += `</ul>
      </div>`;
  }
  
  // Next Steps based on standard AND scores (Without timeline)
  analysisHTML += `
    <div class="next-steps">
      <h4>🎯 Your Next Steps (${standard} Standard)</h4>`;
  
  if (standard === "10th") {
    const hasWeakSubjects = data.strength_analysis.weak_subjects && data.strength_analysis.weak_subjects.length > 0;
    const hasStrongSubjects = data.strength_analysis.strong_subjects && data.strength_analysis.strong_subjects.length > 0;
    
    if (hasWeakSubjects) {
      analysisHTML += `
        <div class="alert urgent-alert">
          <h5>⚠️ Priority Action Required</h5>
          <p>Your weak subjects (${data.strength_analysis.weak_subjects.join(', ')}) need immediate attention before stream selection.</p>
          <ul>
            <li>Get tutoring for weak subjects immediately</li>
            <li>Don't choose stream until weak subjects improve</li>
            <li>Focus 60% study time on weak subjects</li>
          </ul>
        </div>`;
    }
    
    if (hasStrongSubjects) {
      analysisHTML += `
        <div class="alert success-alert">
          <h5>✅ Your Advantages</h5>
          <p>Your strong subjects (${data.strength_analysis.strong_subjects.join(', ')}) give you an edge in these streams:</p>
          <ul>
            <li><strong>Science Stream:</strong> If strong in Science & Maths</li>
            <li><strong>Commerce Stream:</strong> If strong in Maths & English</li>
            <li><strong>Arts Stream:</strong> If strong in English & Creative</li>
          </ul>
        </div>`;
    }
    
  } else if (standard === "12th") {
    const pcmAvg = data.strength_analysis.strong_subjects && 
                   (data.strength_analysis.strong_subjects.includes('Physics') || 
                    data.strength_analysis.strong_subjects.includes('Chemistry') || 
                    data.strength_analysis.strong_subjects.includes('Maths'));
    
    const pcbAvg = data.strength_analysis.strong_subjects && 
                   (data.strength_analysis.strong_subjects.includes('Physics') || 
                    data.strength_analysis.strong_subjects.includes('Chemistry') || 
                    data.strength_analysis.strong_subjects.includes('Biology'));
    
    if (pcmAvg) {
      analysisHTML += `
        <div class="alert engineering-alert">
          <h5>⚙️ Engineering Path Available</h5>
          <p>Your strong PCM subjects qualify you for engineering entrance exams.</p>
          <ul>
            <li><strong>JEE Mains:</strong> Minimum preparation: 6 months intensive</li>
            <li><strong>State CETs:</strong> Preparation: 3-4 months</li>
            <li><strong>BITSAT:</strong> Additional physics/chemistry focus needed</li>
          </ul>
        </div>`;
    }
    
    if (pcbAvg) {
      analysisHTML += `
        <div class="alert medical-alert">
          <h5>🏥 Medical Path Available</h5>
          <p>Your strong PCB subjects qualify you for medical entrance exams.</p>
          <ul>
            <li><strong>NEET:</strong> Minimum preparation: 8 months with biology focus</li>
            <li><strong>AIIMS:</strong> Additional general knowledge preparation</li>
            <li><strong>State Medical Exams:</strong> Vary by state requirements</li>
          </ul>
        </div>`;
    }
  }
  
  analysisHTML += `</div>`;
  
  // Save Results with personalized filename
  const user = JSON.parse(localStorage.getItem("user")) || { name: "Student" };
  const dateStr = new Date().toISOString().slice(0, 10);
  
  analysisHTML += `
    <div class="save-results">
      <button onclick="savePersonalizedAnalysis('${standard}', '${user.name}', '${dateStr}')" class="save-btn">
        💾 Save Your Personalized Analysis
      </button>
      <p class="save-note">This analysis is 100% unique to you. Save it to track progress and share with counselors.</p>
    </div>`;
  
  analysisHTML += `</div>`;
  
  analysisElement.innerHTML = analysisHTML;
  
  // Add smooth scrolling
  setTimeout(() => {
    analysisElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

// ===============================
// SAVE PERSONALIZED ANALYSIS
// ===============================
function savePersonalizedAnalysis(standard, userName, dateStr) {
  const analysisElement = standard === "10th" 
    ? document.getElementById('tenthAnalysis') 
    : document.getElementById('twelfthAnalysis');
  
  if (!analysisElement || analysisElement.innerHTML === '') {
    alert("No analysis results to save!");
    return;
  }
  
  // Create a printable version with all personalization
  const printContent = analysisElement.innerHTML;
  const fullContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>100% Personalized Career Analysis - ${userName} (${standard})</title>
      <style>
        body { 
          font-family: Arial, sans-serif; 
          padding: 25px; 
          max-width: 1000px;
          margin: 0 auto;
          background: #f8f9ff;
        }
        h2, h3, h4 { color: #6a11cb; }
        .profile-summary { 
          background: linear-gradient(135deg, #6a11cb, #2575fc);
          color: white;
          padding: 20px;
          border-radius: 10px;
          margin: 20px 0;
        }
        .career-card { 
          border: 1px solid #ddd; 
          padding: 20px; 
          margin: 15px 0; 
          border-radius: 10px;
          background: white;
          box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        .top-career { 
          border: 3px solid #6a11cb;
          background: linear-gradient(135deg, #f8f9ff, #e8edff);
        }
        .urgent-action { 
          background: #ffeaea;
          border-left: 4px solid #ff6b6b;
          padding: 10px;
          margin: 8px 0;
          border-radius: 5px;
        }
        .academic-action { 
          background: #e8f4ff;
          border-left: 4px solid #2575fc;
          padding: 10px;
          margin: 8px 0;
          border-radius: 5px;
        }
        .alert { 
          padding: 15px;
          margin: 15px 0;
          border-radius: 8px;
          border-left: 5px solid;
        }
        .urgent-alert { 
          background: #ffeaea;
          border-left-color: #ff6b6b;
        }
        .engineering-alert { 
          background: #e8f4ff;
          border-left-color: #2575fc;
        }
        .medical-alert { 
          background: #e8fff4;
          border-left-color: #00b894;
        }
        .score-badge, .trait-badge { 
          display: inline-block;
          padding: 5px 10px;
          margin: 5px;
          border-radius: 20px;
          font-size: 14px;
        }
        .excellent { background: #d4edda; color: #155724; }
        .average { background: #fff3cd; color: #856404; }
        .weak { background: #f8d7da; color: #721c24; }
        .strong { background: #cce5ff; color: #004085; }
        @media print {
          .save-btn { display: none; }
          body { background: white; }
        }
      </style>
    </head>
    <body>
      <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #6a11cb; padding-bottom: 20px;">
        <h1 style="color: #6a11cb;">100% Personalized Career Analysis Report</h1>
        <p><strong>Student:</strong> ${userName}</p>
        <p><strong>Standard:</strong> ${standard}</p>
        <p><strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}</p>
        <p style="color: #666; font-style: italic;">This analysis is uniquely generated based on your specific scores, personality traits, and interests.</p>
      </div>
      
      <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        ${printContent}
      </div>
      
      <div style="margin-top: 30px; padding: 20px; background: #f8f9ff; border-radius: 10px; text-align: center;">
        <h3>📋 How to Use This Report</h3>
        <ol style="text-align: left; display: inline-block;">
          <li><strong>Review Urgent Actions:</strong> Start with the red/high-priority items</li>
          <li><strong>Create Study Plan:</strong> Based on academic improvement suggestions</li>
          <li><strong>Track Progress:</strong> Revisit this report monthly to check progress</li>
          <li><strong>Consult Counselors:</strong> Share this report with career counselors</li>
          <li><strong>Update Regularly:</strong> Get new analysis when scores improve</li>
        </ol>
      </div>
      
      <footer style="margin-top: 40px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; padding-top: 20px;">
        <p>Generated by AI Career Path Allocator • ${new Date().toLocaleString()}</p>
        <p>This is a personalized analysis. For official counseling, consult certified career counselors.</p>
      </footer>
    </body>
    </html>
  `;
  
  // Create download link
  const blob = new Blob([fullContent], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Personalized_Career_Analysis_${userName.replace(/\s+/g, '_')}_${standard}_${dateStr}.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  alert("✅ Your 100% personalized analysis has been saved!\n\nYou can:\n1. Open the file to review\n2. Print it for reference\n3. Share with parents/teachers\n4. Use it to track your progress");
}


// ===============================
// 10TH STANDARD PREDICTION
// ===============================
async function predictTenthCareer() {
  const progressContainer = document.getElementById('tenthProgressContainer');
  const progressBar = document.getElementById('tenthProgressBar');
  const resultElement = document.getElementById('tenthResult');
  
  // Show loading state
  progressContainer.classList.add('show');
  progressBar.style.width = '0%';
  resultElement.classList.remove('show');
  resultElement.innerHTML = '';
  document.getElementById('tenthAnalysis').innerHTML = '';

  // Get input values
  const science = parseFloat(document.getElementById('tenth_science').value);
  const english = parseFloat(document.getElementById('tenth_english').value);
  const maths = parseFloat(document.getElementById('tenth_maths').value);
  
  // Get psychometric scores
  const analytical_thinking = parseInt(document.getElementById('tenth_analytical_thinking').value);
  const creativity = parseInt(document.getElementById('tenth_creativity').value);
  const leadership = parseInt(document.getElementById('tenth_leadership').value);
  const problem_solving = parseInt(document.getElementById('tenth_problem_solving').value);
  const communication = parseInt(document.getElementById('tenth_communication').value);
  
  // Get interests
  const interest1 = document.getElementById('tenth_interest1').value;
  const interest2 = document.getElementById('tenth_interest2').value;
  const interest3 = document.getElementById('tenth_interest3').value;

  // Validate academic marks
  if (isNaN(science) || isNaN(english) || isNaN(maths)) {
    alert("⚠️ Please fill all marks fields with valid numbers!");
    progressContainer.classList.remove('show');
    return;
  }

  if (science < 0 || science > 100 || english < 0 || english > 100 || maths < 0 || maths > 100) {
    alert("⚠️ All marks must be between 0 and 100!");
    return;
  }

  // Validate psychometric scores
  if (isNaN(analytical_thinking) || isNaN(creativity) || isNaN(leadership) || 
      isNaN(problem_solving) || isNaN(communication)) {
    alert("⚠️ Please rate all psychometric questions (1-5)!");
    return;
  }

  if (!interest1 || !interest2) {
    alert("⚠️ Please select at least two required interests!");
    return;
  }

  // Animate progress bar
  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    progressBar.style.width = `${progress}%`;
    if (progress >= 90) {
      clearInterval(interval);
    }
  }, 200);

  const payload = {
    standard: "10th",
    science,
    english,
    maths,
    analytical_thinking,
    creativity,
    leadership,
    problem_solving,
    communication,
    interest1,
    interest2,
    interest3: interest3 || ""
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    clearInterval(interval);
    progressBar.style.width = '100%';

    const data = await response.json();
    if (data.error) {
      resultElement.innerHTML = `<div class="error-message">❌ <strong>Error:</strong> ${data.error}</div>`;
    } else {
      resultElement.innerHTML = `
        <div class="prediction-result">
          <h3>🎯 AI Career Prediction</h3>
          <div class="primary-career">
            <h4>Recommended Career Path:</h4>
            <p class="career-name">${data.predicted_career}</p>
          </div>
          
          <div class="alternative-careers">
            <h4>Alternative Career Options:</h4>
            <ul>`;
      
      data.top_careers.forEach((career, index) => {
        if (career.career !== data.predicted_career) {
          const probability = (career.probability * 100).toFixed(1);
          resultElement.innerHTML += `
            <li>
              <span class="alt-career-name">${career.career}</span>
              <span class="alt-probability">${probability}% match</span>
            </li>`;
        }
      });
      
      resultElement.innerHTML += `
            </ul>
          </div>
          
          <div class="prediction-note">
            <p>💡 <strong>Tip:</strong> For a detailed analysis with personalized recommendations, try the "Analyze My Strengths" button!</p>
          </div>
        </div>`;
    }
    
    // Show result with animation
    resultElement.classList.add('show');
    
    // Hide progress bar after delay
    setTimeout(() => {
      progressContainer.classList.remove('show');
    }, 1000);

  } catch (err) {
    console.error(err);
    clearInterval(interval);
    progressContainer.classList.remove('show');
    
    // Fallback career prediction
    const fallbackCareer = predictTenthCareerLocal(
      science, english, maths, 
      [interest1, interest2, interest3],
      { analytical_thinking, creativity, leadership, problem_solving, communication }
    );
    
    resultElement.innerHTML = `
      <div class="prediction-result">
        <h3>🎯 Local Career Prediction</h3>
        <div class="primary-career">
          <h4>Recommended Career Path:</h4>
          <p class="career-name">${fallbackCareer}</p>
        </div>
        <div class="prediction-note">
          <p>⚠️ <strong>Note:</strong> Using local prediction as server is unavailable. For detailed analysis, ensure the Flask server is running.</p>
        </div>
      </div>`;
    
    resultElement.classList.add('show');
    
    alert("⚠️ Using local prediction. Flask server might be offline. For full analysis features, please start the server.");
  }
}

// ===============================
// 12TH STANDARD PREDICTION
// ===============================
async function predictTwelfthCareer() {
  const progressContainer = document.getElementById('twelfthProgressContainer');
  const progressBar = document.getElementById('twelfthProgressBar');
  const resultElement = document.getElementById('twelfthResult');
  
  // Show loading state
  progressContainer.classList.add('show');
  progressBar.style.width = '0%';
  resultElement.classList.remove('show');
  resultElement.innerHTML = '';
  document.getElementById('twelfthAnalysis').innerHTML = '';

  // Get input values
  const physics = parseFloat(document.getElementById('twelfth_physics').value);
  const chemistry = parseFloat(document.getElementById('twelfth_chemistry').value);
  const maths = parseFloat(document.getElementById('twelfth_maths').value);
  const biology = parseFloat(document.getElementById('twelfth_biology').value);
  
  // Get psychometric scores
  const analytical_thinking = parseInt(document.getElementById('twelfth_analytical_thinking').value);
  const creativity = parseInt(document.getElementById('twelfth_creativity').value);
  const leadership = parseInt(document.getElementById('twelfth_leadership').value);
  const problem_solving = parseInt(document.getElementById('twelfth_problem_solving').value);
  const communication = parseInt(document.getElementById('twelfth_communication').value);
  
  // Get interests
  const interest1 = document.getElementById('twelfth_interest1').value;
  const interest2 = document.getElementById('twelfth_interest2').value;
  const interest3 = document.getElementById('twelfth_interest3').value;

  // Validate academic marks
  if (isNaN(physics) || isNaN(chemistry) || isNaN(maths) || isNaN(biology)) {
    alert("⚠️ Please fill all marks fields with valid numbers!");
    progressContainer.classList.remove('show');
    return;
  }

  if (physics < 0 || physics > 100 || chemistry < 0 || chemistry > 100 || 
      maths < 0 || maths > 100 || biology < 0 || biology > 100) {
    alert("⚠️ All marks must be between 0 and 100!");
    return;
  }

  // Validate psychometric scores
  if (isNaN(analytical_thinking) || isNaN(creativity) || isNaN(leadership) || 
      isNaN(problem_solving) || isNaN(communication)) {
    alert("⚠️ Please rate all psychometric questions (1-5)!");
    return;
  }

  if (!interest1 || !interest2) {
    alert("⚠️ Please select at least two required interests!");
    return;
  }

  // Animate progress bar
  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    progressBar.style.width = `${progress}%`;
    if (progress >= 90) {
      clearInterval(interval);
    }
  }, 200);

  const payload = {
    standard: "12th",
    physics,
    chemistry,
    maths,
    biology,
    analytical_thinking,
    creativity,
    leadership,
    problem_solving,
    communication,
    interest1,
    interest2,
    interest3: interest3 || ""
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    clearInterval(interval);
    progressBar.style.width = '100%';

    const data = await response.json();
    if (data.error) {
      resultElement.innerHTML = `<div class="error-message">❌ <strong>Error:</strong> ${data.error}</div>`;
    } else {
      resultElement.innerHTML = `
        <div class="prediction-result">
          <h3>🎯 AI Career Prediction</h3>
          <div class="primary-career">
            <h4>Recommended Career:</h4>
            <p class="career-name">${data.predicted_career}</p>
          </div>
          
          <div class="alternative-careers">
            <h4>Alternative Career Options:</h4>
            <ul>`;
      
      data.top_careers.forEach((career, index) => {
        if (career.career !== data.predicted_career) {
          const probability = (career.probability * 100).toFixed(1);
          resultElement.innerHTML += `
            <li>
              <span class="alt-career-name">${career.career}</span>
              <span class="alt-probability">${probability}% match</span>
            </li>`;
        }
      });
      
      resultElement.innerHTML += `
            </ul>
          </div>
          
          <div class="prediction-note">
            <p>💡 <strong>Tip:</strong> For a detailed analysis with personalized recommendations, try the "Analyze My Strengths" button!</p>
          </div>
        </div>`;
    }
    
    // Show result with animation
    resultElement.classList.add('show');
    
    // Hide progress bar after delay
    setTimeout(() => {
      progressContainer.classList.remove('show');
    }, 1000);

  } catch (err) {
    console.error(err);
    clearInterval(interval);
    progressContainer.classList.remove('show');
    
    // Fallback career prediction
    const fallbackCareer = predictTwelfthCareerLocal(
      physics, chemistry, maths, biology,
      [interest1, interest2, interest3],
      { analytical_thinking, creativity, leadership, problem_solving, communication }
    );
    
    resultElement.innerHTML = `
      <div class="prediction-result">
        <h3>🎯 Local Career Prediction</h3>
        <div class="primary-career">
          <h4>Recommended Career:</h4>
          <p class="career-name">${fallbackCareer}</p>
        </div>
        <div class="prediction-note">
          <p>⚠️ <strong>Note:</strong> Using local prediction as server is unavailable. For detailed analysis, ensure the Flask server is running.</p>
        </div>
      </div>`;
    
    resultElement.classList.add('show');
    
    alert("⚠️ Using local prediction. Flask server might be offline. For full analysis features, please start the server.");
  }
}

// ===============================
// LOCAL FALLBACK PREDICTIONS
// ===============================
function predictTenthCareerLocal(science, english, maths, interests, psychometric) {
  const avgMarks = (science + english + maths) / 3;
  const psychometricScore = (
    psychometric.analytical_thinking + 
    psychometric.creativity + 
    psychometric.leadership + 
    psychometric.problem_solving + 
    psychometric.communication
  ) / 5;
  
  if (avgMarks >= 85 && psychometricScore >= 4) {
    if (interests.includes('Technology') || interests.includes('Engineering')) 
      return "Engineering Stream (PCM)";
    if (interests.includes('Science') || interests.includes('Healthcare')) 
      return "Medical Stream (PCB)";
  } else if (avgMarks >= 70 && psychometricScore >= 3.5) {
    if (interests.includes('Technology') && psychometric.analytical_thinking >= 4) 
      return "Engineering Stream (PCM)";
    if (interests.includes('Business') && psychometric.communication >= 4) 
      return "Commerce Stream";
    if (interests.includes('Science') && psychometric.problem_solving >= 4) 
      return "Medical Stream (PCB)";
  } else if (avgMarks >= 60) {
    if (interests.includes('Arts') || interests.includes('Creative')) 
      return "Arts/Humanities Stream";
    if (interests.includes('Business') || interests.includes('Finance')) 
      return "Commerce Stream";
  } else {
    if (psychometric.creativity >= 4) return "Arts/Humanities Stream";
    if (psychometric.leadership >= 4) return "Commerce Stream";
    return "Vocational Studies";
  }
  
  return "General Degree Courses";
}

function predictTwelfthCareerLocal(physics, chemistry, maths, biology, interests, psychometric) {
  const pcmAvg = (physics + chemistry + maths) / 3;
  const pcbAvg = (physics + chemistry + biology) / 3;
  const psychometricScore = (
    psychometric.analytical_thinking + 
    psychometric.creativity + 
    psychometric.leadership + 
    psychometric.problem_solving + 
    psychometric.communication
  ) / 5;
  
  if (pcmAvg >= 85 && psychometricScore >= 4) {
    if (interests.includes('Engineering') && psychometric.analytical_thinking >= 4) 
      return "Software Engineer";
    if (interests.includes('Technology') && psychometric.problem_solving >= 4) 
      return "Data Scientist";
    return "Civil Engineer";
  } else if (pcbAvg >= 85 && psychometricScore >= 4) {
    if ((interests.includes('Medical') || interests.includes('Healthcare')) && psychometric.communication >= 4) 
      return "Doctor";
    if (interests.includes('Research') && psychometric.analytical_thinking >= 4) 
      return "Research Scientist";
    return "Doctor";
  } else if ((pcmAvg >= 70 || pcbAvg >= 70) && psychometricScore >= 3.5) {
    if (interests.includes('Engineering')) return "Civil Engineer";
    if (interests.includes('Medical')) return "Medical Technician";
    if (interests.includes('Business') && psychometric.leadership >= 4) return "Financial Analyst";
  } else {
    if (interests.includes('Arts') && psychometric.creativity >= 4) return "Graphic Designer";
    if (interests.includes('Law') && psychometric.communication >= 4) return "Lawyer";
    return "Journalist";
  }
  
  return "General Degree Programs";
}

// ===============================
// LOGOUT FUNCTION
// ===============================
function logout() {
  localStorage.removeItem("user");
  window.location.href = "login.html";
}