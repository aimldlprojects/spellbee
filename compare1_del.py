# List top 10 wrongly spelled words
# Initialize DataFrame to store top 10 wrongly spelled words
top_wrong_words_df = pd.DataFrame(columns=['user', 'word_type', 'word_length', 'word', 'incorrect_attempt_count', 'correct_attempt_count'])
# user_wrong_words_df = pd.DataFrame(columns=['user', 'word_type', 'word_length', 'word', 'incorrect_attempt_count', 'correct_attempt_count'])

for user in users:
    df = words_df[(words_df['user']==user) | (words_df['user']=='User')].reset_index(drop=True)
    
    df = df[~df['word'].isin(remove_unwanted_words_df['unwanted_words'])]
    df = df[~df['word'].isin(review_words_df['review_word'])]
    df['word_len'] = df['word'].apply(len)

    word_type_list = list(df['word_type'].unique())
    unique_lengths = set(df['word'].apply(len))
    unique_lengths_list = list(unique_lengths)

    correct_words_filename = f"user_{user}_correct_words.csv"
    incorrect_words_filename = f"user_{user}_incorrect_words.csv"

    cols = ['user', 'word', 'datetime', 'word_type']
    correct_words_df = pd.read_csv(correct_words_filename, names=cols)
    incorrect_words_df = pd.read_csv(incorrect_words_filename, names=cols)
    correct_words_df['word_len'] = correct_words_df['word'].apply(len)
    incorrect_words_df['word_len'] = incorrect_words_df['word'].apply(len)
    
    # Get top 10 wrongly spelled words per user, per word_type, per word length
    for word_type in word_type_list:
        for word_len in unique_lengths_list:
            # Filter words by word_type and word length
            incorrect_words_filtered = incorrect_words_df[(incorrect_words_df['word_type'] == word_type) & 
                                                     (incorrect_words_df['word_len'] == word_len)]
            correct_words_filtered = correct_words_df[(correct_words_df['word_type'] == word_type) & 
                                                      (correct_words_df['word_len'] == word_len)]
            # Get count of each word
            incorrect_words_word_counts = incorrect_words_filtered['word'].value_counts(ascending=False)
            correct_words_word_counts = correct_words_filtered['word'].value_counts(ascending=False)
            
            # Get top 10 wrongly spelled words
            top_wrong_words = incorrect_words_word_counts.head(10) # set how many words to get for each type

            # Create DataFrame for top 10 wrongly spelled words
            top_wrong_words_data = []
            for word, count in top_wrong_words.items():
                correct_attempt_count = correct_words_word_counts.get(word, 0)
                top_wrong_words_data.append({'user': user,
                                              'word_type': word_type,
                                              'word_length': word_len,
                                              'word': word,
                                              'incorrect_attempt_count': count,
                                              'correct_attempt_count': correct_attempt_count})
   
            # Append results for the current word_type and word_len to user_wrong_words_df
            word_type_len_df = pd.DataFrame(columns=['user', 'word_type', 'word_length', 'word', 'incorrect_attempt_count', 'correct_attempt_count'])
            word_type_len_df = pd.concat([word_type_len_df, pd.DataFrame(top_wrong_words_data)])
            word_type_len_df = word_type_len_df.sort_values(by='incorrect_attempt_count', ascending=False)
   

            top_wrong_words_df = pd.concat([top_wrong_words_df, word_type_len_df])


# Save top 10 wrongly spelled words to CSV
top_wrong_words_df.to_csv('word_stats_top_wrong_words.csv', index=False)

top_wrong_words_df
