# spellbee
## App Functionality
---

### **Algorithm for the Spelling Bee Application**

#### **1. Load Application Configuration**
- **Step 1.1**: Load the `word_list_all.csv` file into a Pandas DataFrame at the application startup.
- **Step 1.2**: Define separate CSV files for storing user-specific data:
  - `user_{user_id}_correct_words.csv`
  - `user_{user_id}_incorrect_words.csv`
  - `review_words.csv`
- **Step 1.3**: Load configurations such as:
  - User IDs.
  - Test Types: "Unattended words," "Previous incorrectly spelled words," "Words practiced a week ago."
  - Word Types: List of all unique values in the word_type column of loaded and filtered data based on the test type from `word_list_all.csv`.
  - Word Lengths: List of all unique values of length of different words in loaded and filtered data based on the test type & word type of `word_list_all.csv`.
  - Note: While Loading data with test Type or Word Types or Word Length filter options, always drop word that are in `review_words.csv` from `word_list_all.csv` in the first step itself.

---

#### **2. UI Initialization**
- **Step 2.1**: Design the UI with the following components:
  - Dropdown Menus: User ID, Test Type, Word Type, Word Length.
  - Buttons: `Start Test`, `Check`, `Next Word`, `Review Word`, `Hear Word`.
  - Checkboxes: `Pronounce Sentence`, `Auto Advance`, `Hide Test Options`.
  - Text Inputs: `User Input Entry` for word spellings.
  - Labels: App Title, Instruction Label, Current Word Label, Status Label.
  - Side Panel: For test options.
  - Sidebar Separator: Separates test options from the main content.
- **Step 2.2**: Bind dropdowns, buttons, and checkboxes to their respective functions (e.g., filters, test initiation).

---

#### **3. Load and Filter Word List**
- **Step 3.1**: When the `User ID` is selected, load the data from the `word_list_all.csv` to `word_list` dataframe and then filter data by `user_id` to load user-specific word data. Match the values of user column with `user_id`. save this data to `word_list_user` dataframe.
- **Step 3.2**: Apply **Test Type Filters**:
  - **Unattended Words**: 
    - Filter out words that exist in `user_{user_id}_correct_words.csv` and `review_words.csv` from `word_list_user` dataframe.
  - **Previous Incorrectly Spelled Words**: 
    - Include words only in `user_{user_id}_incorrect_words.csv`, excluding those in `review_words.csv` from `word_list_user` dataframe.
  - **Words Practiced a Week Ago**: 
    - Select words practiced >7 days ago in `user_{user_id}_correct_words.csv` and `user_{user_id}_incorrect_words.csv`, excluding those in `review_words.csv` from `word_list_user` dataframe.
  - Save this data as `word_list_test_type` dataframe.
- **Step 3.3**: Apply **Word Type Filter** based on the selected `word_type` column. Match the selected values with word_type colume values in `word_list_test_type` dataframe and save the data to `word_list_word_type` dataframe.
- **Step 3.4**: Apply **Word Length Filter** based on the length of words. Match the selected values with word length of the words that are in word column of `word_list_word_type` dataframe and save it to `word_list_word_len` dataframe.
- **Step 3.5**: Ensure filters are applied in sequence: **Test Type → Word Type → Word Length**.

---

#### **4. Test Initialization**
- **Step 4.1**: On clicking the `Start Test` button:
  - Shuffle the filtered word list.
  - Pick the first word randomly.
  - Display the current word (masked) and play the pronunciation and related sentence (if `Pronounce Sentence` is checked).
  - Update the `Current Word Label` with the word count and the `Instruction Label` with guidelines.

---

#### **5. Test Progression**
- **Step 5.1**: **Hear Word**: Replay the word and sentence pronunciation when the `Hear Word` button is clicked.
- **Step 5.2**: **User Input**:
  - User enters the spelling in the `User Input Entry`.
  - On clicking the `Check` button:
    - Compare the user’s input with the correct spelling.
    - If correct:
      - Save the word in `user_{user_id}_correct_words.csv`.
      - Remove the word from the current word list.
      - Update the status message: "Correct!".
    - If incorrect:
      - Save the word in `user_{user_id}_incorrect_words.csv`.
      - Display the correct spelling in the status message: "Incorrect! Correct spelling is [correct_word].".
    - Update the `Status Label` with the current and total test scores.
  - If `Auto Advance` is checked, wait 2 seconds and move to the next word.
- **Step 5.3**: **Next Word**:
  - On clicking the `Next Word` button:
    - Randomly pick another word from the current word list.
    - Display the next word (masked).
    - No score is updated for skipped words.
- **Step 5.4**: **Review Word**:
  - On clicking the `Review Word` button:
    - Save the word in `review_words.csv`.
    - Remove the word from the current word list.
    - Pick the next word automatically.
- **Step 5.5**: **Auto Advance**: Automatically proceed to the next word after 2 seconds if the feature is enabled.

---

#### **6. Test Completion**
- **Step 6.1**: The test ends when all words from the filtered list are exhausted.
- **Step 6.2**: Display the final score summary:
  - Correct words.
  - Incorrect words.
  - Words marked for review.
- **Step 6.3**: Save the test results to a session-specific file for analytics.

---

#### **7. Additional Features**
- **Step 7.1**: **Hide Test Options**: If the checkbox is checked, hide the side panel with filters and test options.
- **Step 7.2**: Add a progress bar to visually represent test completion.
- **Step 7.3**: Add analytics (optional):
  - Word accuracy rates.
  - Weekly progress tracking.
- **Step 7.4**: Add a settings panel to manage users, word list updates, and file paths.

---

#### **8. Error Handling**
- **Step 8.1**: Validate user input for empty or invalid characters.
- **Step 8.2**: Handle cases where no words are left after applying filters.
- **Step 8.3**: Log errors in a separate log file for debugging.

---

#### **9. App Shutdown**
- Save the current state (e.g., progress, filters) to allow resuming later.
- Close all open file handles and clear temporary variables.


---
''' This app is for testing the spelling capabilities of the users. word_list.csv is the file which contains the words that are to be tested.
The app has a UI which has the following features:
    User ID dropdown menu to show the list of user. 
    Test Type dropdown menu to show the list of test types.
    Word Type dropdown menu to show the list of word types.
    Word Length dropdown menu to show the list of word lengths.
    Start Test button to start the test.
    Check button to check the spelling of the word.
    Next Word button to move to the next word.
    Review Word button to review the word.
    Pronounce Sentence checkbox to pronounce the word and releated sentence.
    Auto Advance checkbox to automatically advance to the next word after showing status message for 2 seconds. status message will show the correct or wrong spelling of the word.
    Hide Test Options checkbox to hide the test options.
    Hear Word button to hear the word.
    User input entry to enter the spelling of the word.
    Status label to show the current and total test scores.
    Current word label to show the current word to spell.
    Instruction label to show the instruction to the user.
    App title to show the title of the app.
    Sidebar separator to separate the sidebar from the main content.
    Side panel for test options to show the test options.

Logic:
    The app will load the word list from the word_list.csv file. 
    The user can select the user ID, test type, word type, and word length from the dropdown menus. 
    Based on the selected user, the word list will be loaded by applying the filter of the user column = user id.
    The user can further apply the filter on the loaded words on Test Type.
    if test type is selected as Unattended words, the app will filter out the Unattended answered words from the word_list_all.csv by droping all words that are in f'user_{user_id}_correct_words.csv' and word that are in 'review_words.csv' from word_list_all.csv.
    if test type is selected as Previous incorrectly spelled words, the app will filter words in word_list_all.csv and that are in f'user_{user_id}_incorrect_words.csv'. It also drops the words that are in and word that are in 'review_words.csv' from word_list_all.csv.
    if test type is selected as Words practiced a week ago, the app will filter out the words that are practiced more than a week ago from f'user_{user_id}_correct_words.csv' and f'user_{user_id}_incorrect_words.csv' and pick those words from  word_list_all.csv. It also drops the words that are in and word that are in 'review_words.csv' from word_list_all.csv.
    The user can further apply the filter on the loaded words on Word Type. data will be filtered based on the selected word type that matches values in the word_type column of the word_list_all.csv. if all is selected, no filter will be applied.
    The user can further apply the filter on the loaded words on Word Length. data will be filtered based on the selected word length that matches the length of the words in the word_list_all.csv. if all is selected, no filter will be applied.
    All these filters are dependent on previous filters. in sequence first test type is applied for filter and on the filtered data word type filter is applied and on the filtered data word length filter is applied.
    The dropdown menus are binded with the update functions to update the word list based on the selected values from previous filters. 
    The user can start the test by clicking the Start Test button. 
    The app will randomly pick word from filtered words of word_list_all.csv and show the that word as a current word and speak the word and releated sentance. the app will show releated sentance as the masked sentence examples. 
    The user can hear again the word by clicking the Hear Word button. 
    The user can enter the spelling of the word in the user input entry. 
    The user can check the spelling by clicking the Check button. 
    The app will show the status message with the correct or wrong spelling of the word. 
    if the spelling is correct, the app will remove the word from the loaded word list object and save the word in f'user_{user_id}_correct_words.csv' file.
    if the spelling is wrong, the app will save the word in f'user_{user_id}_incorrect_words.csv' file.
    The app will show the correct spelling of the word in the status message if the spelling is wrong.
    The app will show the remaining words count in the current word label.
    The app will automatically advance to the next word after showing the status message for 2 seconds if the Auto Advance checkbox is checked. 
    The user can move to the next word by clicking the Next Word button. It will not have any impact on the test scores. The word will retested again based on the random pick.
    The user can review the word by clicking the Review Word button. The word will be saved in the review_words.csv file and removed from the current word list.
    The user can hear the word and related sentence by checking the Pronounce Sentence checkbox. 
    The user can hide the test options by checking the Hide Test Options checkbox. 
    The app will show the current and total test scores in the status label. 
    The app will show the instruction to the user in the instruction label. 
    The app will show the title of the app in the app title. 
    The app will separate the sidebar from the main content using the sidebar separator. 
    The app will show the test options in the side panel.


'''
