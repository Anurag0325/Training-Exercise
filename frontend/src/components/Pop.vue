<template>
    <div v-if="showPopup" class="popup">
        <div class="popup-content">
            
            <div v-if="showStudyMaterial && !showQuestions" ref="studyMaterialSection">
                <h2 class="popup-title">Study Material</h2>

                <div class="content-section">
                    <h3 class="section-title">Course Content</h3>
                    <ul class="content-list">
                        <li class="content-item">1. What is Phishing?</li>
                        <li class="content-item">2. Common Phishing Techniques</li>
                        <li class="content-item">3. How to Recognize Phishing Emails</li>
                        <li class="content-item">4. Best Practices for Online Safety</li>
                    </ul>
                </div>

                <!-- Video Section (Google Slide presentation) -->
                <div class="video-section">
                    <h3 class="video-title">Cyber Security Training Tutorial</h3>
                    <iframe
                        ref="presentationIframe" 
                        src="https://docs.google.com/presentation/d/e/2PACX-1vSkHqHBoKf3xM2yy9QMU-98GbyywQACmHqLX2Uno-xI1zDcIWckVC8_PjYqO34UW2RGMbFqZgnCc170/embed?start=true&loop=false&delayms=3000" 
                        frameborder="0"
                        class="presentation-iframe" 
                        allowfullscreen
                        mozallowfullscreen 
                        webkitallowfullscreen>
                    </iframe>
                </div>

                <button 
                    class="button-primary" 
                    :disabled="isButtonDisabled || !isPresentationCompleted"  
                    @click="fetchQuestions">
                    <span v-if="isButtonDisabled">Loading...</span>  <!-- Loading state -->
                    <span v-else>Start Quiz</span>
                </button>
            </div>

            <!-- Quiz Section -->
            <div v-if="showQuestions" class="questions-container">
                <h2 class="popup-title">Quiz: Phishing Awareness</h2>
                <div class="questions-wrapper">
                    <!-- <div v-for="(question, index) in questions" :key="index" class="question"> -->
                    <div v-for="(question, index) in selectedQuestions" :key="index" class="question">
                        <p class="question-text">{{ question.question_text }}</p>
                        <ul class="options-list">
                            <li v-for="(option, idx) in question.options" :key="idx" class="option-item">
                                <label class="option-label">
                                    <input type="radio" :name="'question_' + index" :value="option" v-model="answers[index]" />
                                    {{ option }}
                                </label>
                            </li>
                        </ul>
                    </div>
                </div>
                <button class="button-primary" @click="submitAnswers">Submit Answers</button>
            </div>

            <div v-if="showScoreSection" class="score-container">
                <h3 class="score-text">You scored {{ score }}%.</h3>

                <div v-if="score >= 70">
                    <p>Thank you for participating in the data phishing awareness program. Soon you will get your result.</p>
                    <button class="button-primary" @click="closePopup">
                        Close
                    </button>
                </div>

                <div v-else>
                    <button class="button-secondary" @click="redoQuiz">
                        Redo Quiz
                    </button>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
export default {

    props: {
       colleague_id: {
           type: String,
           required: true,
       },
   },

   
    data() {
        return {
            showPopup: false,
            showStudyMaterial: true,
            showQuestions: false,
            showCloseButton: false,
            questions: [],
            answers: [],
            isPresentationCompleted: false,
            score: 0,
            showScoreSection: false,
            colleague_id: null,
            isButtonDisabled: false,
        };
    },

    created() {
        const colleagueId = this.$route.params.colleague_id;
        this.fetchData(colleagueId);

        // Check if the route is for study material
        if (this.$route.path.startsWith('/study-material')) {
            this.showStudyMaterial = true; // Open the study material section directly
            this.trackPresentationCompletion();
        }
    },

    mounted() {
        this.colleague_id = this.$route.params.colleague_id;
        this.trackPresentationCompletion();
    },

    methods: {

        async fetchData(colleagueId) {
            console.log('Fetching data for colleague ID:', colleagueId); // Check what ID is being sent
            try {
                // const response = await fetch(`https://phishing-mail-application.onrender.com/phishing_opened/${colleagueId}`);
                const response = await fetch(`http://127.0.0.1:5000/phishing_opened/${colleagueId}`);
                const data = await response.json();
                console.log('Response data:', data); // Log the response data
                if (data.showPopup) {
                    this.showPopup = true;
                } else {
                    this.showPopup = false;
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },

        startTutorial() {
            this.showStudyMaterial = true;
            this.$nextTick(() => {
                this.enterFullScreen();
                this.trackPresentationCompletion();
            });
        },
        enterFullScreen() {
            const studyMaterialSection = this.$refs.studyMaterialSection;

            if (studyMaterialSection && studyMaterialSection.requestFullscreen) {
                studyMaterialSection.requestFullscreen();
            } else if (studyMaterialSection && studyMaterialSection.mozRequestFullScreen) {
                studyMaterialSection.mozRequestFullScreen();
            } else if (studyMaterialSection && studyMaterialSection.webkitRequestFullscreen) {
                studyMaterialSection.webkitRequestFullscreen();
            } else if (studyMaterialSection && studyMaterialSection.msRequestFullscreen) {
                studyMaterialSection.msRequestFullscreen();
            } else {
                console.warn("Full screen is not supported");
            }
            document.addEventListener('keydown', this.preventEsc);
        },
        preventEsc(event) {
            if (event.key === "Escape") {
                event.preventDefault();
            }
        },

        trackPresentationCompletion() {
            const presentationDuration = 5000;
            this.isButtonDisabled = true;
            setTimeout(() => {
                this.isButtonDisabled = false;
                this.isPresentationCompleted = true;
            }, presentationDuration);
        },

        async fetchQuestions() {
            try {
                // const response = await fetch('https://phishing-mail-application.onrender.com/get_random_questions');
                const response = await fetch('http://127.0.0.1:5000/get_random_questions');
                if (!response.ok) {
                    throw new Error('Failed to fetch questions');
                }
                const data = await response.json();
                this.selectedQuestions = data.questions; // Store fetched questions in a variable
                this.answers = Array(this.selectedQuestions.length).fill(null); // Initialize answers array
                this.showQuestions = true;
            } catch (error) {
                console.error('Error fetching questions:', error);
            }
        },

        async submitAnswers() {
            try {
                let score = 0;
                const totalQuestions = this.selectedQuestions.length; // Use selectedQuestions here

                // Check answers and calculate score
                this.answers.forEach((answer, index) => {
                    if (answer === this.selectedQuestions[index].correct_answer) {
                        score++;
                    }
                });

                // Send answers and score to the backend
                // const response = await fetch(`https://phishing-mail-application.onrender.com/submit_answers/${this.colleague_id}`, {
                const response = await fetch(`http://127.0.0.1:5000/submit_answers/${this.colleague_id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        answers: this.answers,
                        score: score,
                        questions: this.selectedQuestions // Send the fetched questions to compare the answers
                    })
                });

                const result = await response.json();
                if (response.ok) {
                    console.log(result.message);
                    this.showScoreSection = true;
                    this.score = result.score;
                    this.showQuestions = false;
                    this.showStudyMaterial = false;
                    this.showCloseButton = true;
                } else {
                    console.error('Error submitting answers:', result.error);
                }
            } catch (error) {
                console.error('Error submitting answers:', error);
            }
        },


        async updateReportStatus(colleagueId, score) {
            try {
                // const response = await fetch(`https://phishing-mail-application.onrender.com/update_report_status/${colleagueId}`, {
                const response = await fetch(`http://127.0.0.1:5000/update_report_status/${colleagueId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        score: score,  // Send the score to be updated in the database
                    }),
                });
                if (!response.ok) {
                    throw new Error('Failed to update report status');
                }
                console.log('Report status updated successfully');
            } catch (error) {
                console.error('Error updating report status:', error);
            }
        },

        async downloadPDF(colleagueId) {
            try {
                // const response = await fetch(`https://phishing-mail-application.onrender.com/download_certificate/${colleagueId}`);
                const response = await fetch(`http://127.0.0.1:5000/${colleagueId}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `certificate_${this.colleague_id}.pdf`; // Dynamic filename
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error downloading PDF:', error);
            }
        },


        async redoQuiz() {
            this.showScoreSection = false;
            this.showQuestions = true; // Hide the score section

            // Clear previous answers
            this.answers = Array(this.selectedQuestions.length).fill(null); // Reset answers array

            try {
                // Fetch a new set of random questions
                // const response = await fetch('https://phishing-mail-application.onrender.com/get_random_questions');
                const response = await fetch('http://127.0.0.1:5000/get_random_questions');
                if (!response.ok) {
                    throw new Error('Failed to fetch new questions');
                }

                const data = await response.json();
                this.selectedQuestions = data.questions; // Store new questions
                this.showQuestions = true; // Show the questions section again
            } catch (error) {
                console.error('Error fetching new questions:', error);
            }
        },

        gotoclose() {
            this.showScoreSection = false;
            this.showCloseButton = true;
        },

        closePopup() {
            this.showPopup = false;
            window.close();
        },

        async sendEmail(score) {
            const colleagueId = this.$route.params.colleague_id;  // This should be an email, adjust if necessary
            // const studyMaterialLink = `https://phishing-mail-application.onrender.com/study-material/${colleagueId}`;
            const studyMaterialLink = `http://127.0.0.1:5000/study-material/${colleagueId}`;
            const emailContent = score >= 70
                ? { subject: "Training Program Completed", body: `Congratulations on completing the training program! Your score is ${score}.` }
                : { subject: "Training Program Incomplete", body: `You need to reattempt the training program. Your score is ${score}. You can review the study material [here](${studyMaterialLink}).` };

            try {
                // const response = await fetch(`https://phishing-mail-application.onrender.com/send_result_email`, {
                const response = await fetch(`http://127.0.0.1:5000/send_result_email`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        colleague_id: colleagueId,  // Make sure this is the email or use the correct identifier
                        subject: emailContent.subject,
                        body: emailContent.body,
                    }),
                });

                if (!response.ok) {
                    throw new Error('Failed to send email: ' + response.statusText);
                }
                console.log('Email sent successfully');
            } catch (error) {
                console.error('Error sending email:', error);
            }
        }
    }
};
</script>

<style scoped>


.warning-text {
    font-size: 0.9em; 
    color: #333;
    margin: 10px 0;
    line-height: 1.5;
}

.study-material-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.video-section {
    width: 100%;
    margin-bottom: 20px;
}

.content-section {
    text-align: left;
    margin-bottom: 20px;
}

.presentation-iframe {
    width: 100%;
    height: 400px;
    border: none;
}

.section-title {
    font-size: 1.3em; 
    margin-bottom: 10px;
}

.content-list {
    list-style: none;
    padding: 0;
}

.content-item {
    font-size: 0.9em;
    margin: 5px 0;
}

.popup {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
}

.popup-content {
    background: #ffffff;
    border-radius: 16px;
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    padding: 20px;
    text-align: center;
    overflow-y: auto;
    animation: fadeIn 0.3s ease-in-out;
}

.popup-title {
    font-size: 1.8em;
    color: #007bff;
    margin-bottom: 20px;
    font-weight: 700;
}

.questions-container {
    margin-top: 20px;
}

.questions-wrapper {
    text-align: left;
}

.question {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.question-text {
    font-size: 1.2em;
    margin-bottom: 10px;
    font-weight: 600;
}

.options-list {
    list-style: none;
    padding: 0;
}

.option-item {
    margin: 5px 0;
}

.option-label {
    display: flex;
    align-items: center;
    padding: 10px;
    background: #e9ecef;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.2s;
}

.option-label:hover {
    background: #d6d8db;
}

.button-primary, .button-secondary {
    padding: 10px 15px;
    font-size: 1.1em;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 20px;
}

.button-primary {
    background-color: #007bff;
    color: white;
    transition: background 0.2s;
}

.button-primary:hover {
    background-color: #0056b3;
}

.button-secondary {
    background-color: #6c757d;
    color: white;
}

.button-secondary:hover {
    background-color: #5a6268;
}

.button-primary {
    padding: 10px 15px;
    font-size: 1.1em;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 20px;
    background-color: #007bff;
    color: white;
    transition: background 0.2s;
}

.button-primary:disabled {
    background-color: #ccc;
    color: #666;
    cursor: not-allowed;
}

.button-primary:not(:disabled):hover {
    background-color: #0056b3;
}

.alert-popup {
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    max-width: 600px;
    margin: 20px auto;
    text-align: center;
}

.warning-text {
    color: #856404;
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 10px;
}

.blinking {
    animation: blink-animation 1s steps(5, start) infinite;
}

@keyframes blink-animation {
    to {
        visibility: hidden;
    }
}

h1 {
    color: #dc3545; /* Red color for the heading */
    text-align: center;
}

p {
    margin-bottom: 15px;
}

.warning {
   background-color: #ffeeba; /* Light yellow background for the warning */
    border-left: 6px solid #ffc107; /* Yellow border */
    padding: 10px;
    margin: 20px 0;
}

.ria-logo {
    width: 100px;
    height: auto;
}
</style>