package org.implementation.CosineSimilarity;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class callPythonV2 {


    public static String callPythonForPreprocessing(String question) throws IOException {
        String[] command = new String[]{"python", "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Data_Processing/text_cleaning_impl.py", question};
        Process process = Runtime.getRuntime().exec(command);

        BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) {
            output.append(line);
        }
        in.close();

        return output.toString();
    }
}
