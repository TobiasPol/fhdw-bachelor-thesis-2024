def create_model(num_classes):
    sequence_input = Input(shape=(max_sequence_length,), dtype='int32')
    embedded_sequences = Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=32, input_length=max_sequence_length)(sequence_input)
    x = LSTM(units=32, return_sequences=True)(embedded_sequences)
    x = LSTM(units=16)(x)
    additional_input = Input(shape=(len(additional_features[0]),))
    combined = Concatenate()([x, additional_input])
    combined = Dense(units=32, activation='relu')(combined)
    output = Dense(units=num_classes, activation='softmax')(combined)
    model = Model(inputs=[sequence_input, additional_input], outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.001), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model