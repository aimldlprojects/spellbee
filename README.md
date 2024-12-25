# spellbee
## App Functionality

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
