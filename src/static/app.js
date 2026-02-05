document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  
  // Auth elements
  const userIcon = document.getElementById("user-icon");
  const userMenu = document.getElementById("user-menu");
  const loginSection = document.getElementById("login-section");
  const logoutSection = document.getElementById("logout-section");
  const loginBtn = document.getElementById("login-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const loginModal = document.getElementById("login-modal");
  const loginForm = document.getElementById("login-form");
  const loginMessage = document.getElementById("login-message");
  const closeModal = document.querySelector(".close");
  const usernameDisplay = document.getElementById("username-display");
  
  // Registration modal elements
  const registerModal = document.getElementById("register-modal");
  const registerModalClose = document.getElementById("register-modal-close");
  const registerForm = document.getElementById("register-form");
  const registerMessage = document.getElementById("register-message");
  const registerActivityName = document.getElementById("register-activity-name");
  let currentActivityForRegistration = null;
  
  // Auth state
  let isAuthenticated = false;
  let currentUser = null;

  // Authentication functions
  async function checkAuthStatus() {
    try {
      const response = await fetch("/auth/status", {
        credentials: 'include'
      });
      const result = await response.json();
      
      if (result.authenticated) {
        isAuthenticated = true;
        currentUser = result.username;
        updateUIForAuth(true);
      } else {
        isAuthenticated = false;
        currentUser = null;
        updateUIForAuth(false);
      }
    } catch (error) {
      console.error("Error checking auth status:", error);
      isAuthenticated = false;
      updateUIForAuth(false);
    }
  }

  function updateUIForAuth(authenticated) {
    if (authenticated) {
      loginSection.classList.add("hidden");
      logoutSection.classList.remove("hidden");
      usernameDisplay.textContent = `Welcome, ${currentUser}`;
    } else {
      loginSection.classList.remove("hidden");
      logoutSection.classList.add("hidden");
      usernameDisplay.textContent = "";
    }
    // Refresh activities to show/hide delete buttons and register buttons
    fetchActivities();
  }

  // Modal and menu management
  userIcon.addEventListener("click", (e) => {
    e.stopPropagation();
    userMenu.classList.toggle("hidden");
  });

  // Prevent menu from closing when clicking inside it
  userMenu.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  document.addEventListener("click", () => {
    userMenu.classList.add("hidden");
  });

  loginBtn.addEventListener("click", (e) => {
    e.preventDefault();
    loginModal.classList.remove("hidden");
    userMenu.classList.add("hidden");
  });

  closeModal.addEventListener("click", () => {
    loginModal.classList.add("hidden");
    loginForm.reset();
    loginMessage.classList.add("hidden");
  });

  window.addEventListener("click", (event) => {
    if (event.target === loginModal) {
      loginModal.classList.add("hidden");
      loginForm.reset();
      loginMessage.classList.add("hidden");
    }
    if (event.target === registerModal) {
      registerModal.classList.add("hidden");
      registerForm.reset();
      registerMessage.classList.add("hidden");
      currentActivityForRegistration = null;
    }
  });

  // Register modal close handler
  registerModalClose.addEventListener("click", () => {
    registerModal.classList.add("hidden");
    registerForm.reset();
    registerMessage.classList.add("hidden");
    currentActivityForRegistration = null;
  });

  // Login form handler
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch("/auth/login", {
        method: "POST",
        body: formData,
        credentials: 'include'
      });

      const result = await response.json();

      if (response.ok) {
        loginMessage.textContent = result.message;
        loginMessage.className = "success";
        loginMessage.classList.remove("hidden");
        
        setTimeout(() => {
          loginModal.classList.add("hidden");
          loginForm.reset();
          loginMessage.classList.add("hidden");
          checkAuthStatus(); // Refresh auth state
        }, 1000);
      } else {
        loginMessage.textContent = result.detail || "Login failed";
        loginMessage.className = "error";
        loginMessage.classList.remove("hidden");
      }
    } catch (error) {
      loginMessage.textContent = "Network error. Please try again.";
      loginMessage.className = "error";
      loginMessage.classList.remove("hidden");
      console.error("Login error:", error);
    }
  });

  // Logout handler
  logoutBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      const response = await fetch("/auth/logout", {
        method: "POST",
        credentials: 'include'
      });

      if (response.ok) {
        checkAuthStatus(); // Refresh auth state
        userMenu.classList.add("hidden");
      }
    } catch (error) {
      console.error("Logout error:", error);
    }
  });

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons ONLY for authenticated users
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span>${isAuthenticated ? `<button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button>` : ''}</li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        // Add register button for authenticated users
        const registerButtonHTML = isAuthenticated 
          ? `<button class="register-btn" data-activity="${name}">Register Student</button>`
          : '';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
          ${registerButtonHTML}
        `;

        activitiesList.appendChild(activityCard);
      });

      // Add event listeners to delete buttons (only if authenticated)
      if (isAuthenticated) {
        document.querySelectorAll(".delete-btn").forEach((button) => {
          button.addEventListener("click", handleUnregister);
        });
        
        // Add event listeners to register buttons
        document.querySelectorAll(".register-btn").forEach((button) => {
          button.addEventListener("click", handleRegisterClick);
        });
      }
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle register button click
  function handleRegisterClick(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    currentActivityForRegistration = activity;
    registerActivityName.textContent = `Activity: ${activity}`;
    registerModal.classList.remove("hidden");
  }

  // Handle unregister functionality (admin only)
  async function handleUnregister(event) {
    if (!isAuthenticated) {
      alert("You must be logged in as an admin to perform this action.");
      return;
    }

    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
          credentials: 'include'
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, 'success');
        fetchActivities(); // Refresh activities list
      } else if (response.status === 401) {
        showMessage("Authentication required. Please log in.", 'error');
        checkAuthStatus(); // Refresh auth state
      } else {
        showMessage(result.detail || "An error occurred", 'error');
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", 'error');
      console.error("Error unregistering:", error);
    }
  }

  // Handle registration form submission
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!isAuthenticated) {
      alert("You must be logged in as an admin to perform this action.");
      return;
    }

    if (!currentActivityForRegistration) {
      showMessage("No activity selected", 'error');
      return;
    }

    const email = document.getElementById("student-email").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          currentActivityForRegistration
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
          credentials: 'include'
        }
      );

      const result = await response.json();

      if (response.ok) {
        registerMessage.textContent = result.message;
        registerMessage.className = "success";
        registerMessage.classList.remove("hidden");
        
        setTimeout(() => {
          registerModal.classList.add("hidden");
          registerForm.reset();
          registerMessage.classList.add("hidden");
          currentActivityForRegistration = null;
        }, 1500);
        
        fetchActivities(); // Refresh activities list
      } else if (response.status === 401) {
        registerMessage.textContent = "Authentication required. Please log in.";
        registerMessage.className = "error";
        registerMessage.classList.remove("hidden");
        checkAuthStatus(); // Refresh auth state
      } else {
        registerMessage.textContent = result.detail || "An error occurred";
        registerMessage.className = "error";
        registerMessage.classList.remove("hidden");
      }
    } catch (error) {
      registerMessage.textContent = "Failed to register. Please try again.";
      registerMessage.className = "error";
      registerMessage.classList.remove("hidden");
      console.error("Error registering:", error);
    }
  });

  // Helper function to show temporary messages
  function showMessage(message, type) {
    // Create a temporary message element
    const messageEl = document.createElement("div");
    messageEl.className = `message ${type}`;
    messageEl.textContent = message;
    messageEl.style.position = "fixed";
    messageEl.style.top = "20px";
    messageEl.style.right = "20px";
    messageEl.style.zIndex = "3000";
    messageEl.style.maxWidth = "300px";
    
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
      messageEl.remove();
    }, 3000);
  }

  // Initialize app
  checkAuthStatus(); // Check if user is already logged in
  fetchActivities(); // Load activities
});
