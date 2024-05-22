package org.implementation;

import java.util.Arrays;
import java.util.List;

public class BotConfig {
    public static List<String> getJsonFilePaths() {
        return Arrays.asList(
                "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Fitness.json",
                "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Med&Suppl.json",
                "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/MentalHealth.json",
                "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Nutr&Diet.json",
                "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Symp&Cond.json"
        );
    }
}
