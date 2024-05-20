package org.implementation.CosineSimilarity;

import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.RealVector;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public class CosineSimilarity {

    private Map<String, Double> keywordIndexMap;
    private int vectorSize;

    public CosineSimilarity(Set<String> keywords) {
        keywordIndexMap = new HashMap<>();
        vectorSize = keywords.size();
        initializeKeywordIndices(keywords);
    }

    private void initializeKeywordIndices(Set<String> keywords) {
        int index = 0;
        for (String keyword : keywords) {
            keywordIndexMap.put(keyword, (double) index++); // Map each keyword to an index
        }
    }

    public double cosineSimilarity(String[] tokens1, String[] tokens2) {
        RealVector vector1 = toRealVector(tokens1);
        RealVector vector2 = toRealVector(tokens2);
        return (vector1.dotProduct(vector2)) / (vector1.getNorm() * vector2.getNorm());
    }

    private RealVector toRealVector(String[] tokens) {
        RealVector vector = new ArrayRealVector(vectorSize);
        Map<String, Integer> tokenFrequency = new HashMap<>();

        for (String token : tokens) {
            tokenFrequency.put(token, tokenFrequency.getOrDefault(token, 0) + 1);
        }

        for (Map.Entry<String, Double> entry : keywordIndexMap.entrySet()) {
            if (tokenFrequency.containsKey(entry.getKey())) {
                vector.setEntry(entry.getValue().intValue(), tokenFrequency.get(entry.getKey()));
            }
        }

        return vector;
    }
}
