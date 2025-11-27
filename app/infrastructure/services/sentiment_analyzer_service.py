

from typing import Dict, List, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

from app.domain.value_objects import SentimentLabel


class SentimentAnalyzerService:

    
    def __init__(self):

        print(" Inicializando  BERT ")
    
        model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1  
            )
            
            print("BERT cargado exitosamente")
            
        except Exception as e:
            print(f"Error BERT: {e}")
            print("modo fallback (keyword-based)")
            self.sentiment_pipeline = None
    
    async def analyze_sentiment(self, text: str) -> Tuple[SentimentLabel, float, Dict[str, float]]:

        if not text or len(text.strip()) == 0:
            return self._create_neutral_response()
        
        text = self._truncate_text(text, max_tokens=512)
        
        if self.sentiment_pipeline is None:
            return self._analyze_sentiment_fallback(text)
        
        try:
            result = self.sentiment_pipeline(text)[0]

            label, confidence, scores = self._map_bert_result_to_sentiment(result)
            
            return (label, confidence, scores)
        
        except Exception as e:
            print(f"Error en análisis BERT: {e}")
            return self._analyze_sentiment_fallback(text)
    
    async def analyze_batch(
        self,
        texts: List[str],
        max_batch_size: int = 100
    ) -> List[Tuple[SentimentLabel, float, Dict[str, float]]]:

        if len(texts) > max_batch_size:
            raise ValueError(f"Batch size excede el máximo: {max_batch_size}")
        
        results = []
        
        for text in texts:
            result = await self.analyze_sentiment(text)
            results.append(result)
        
        return results
    
    def _map_bert_result_to_sentiment(
        self,
        bert_result: Dict
    ) -> Tuple[SentimentLabel, float, Dict[str, float]]:

        bert_label = bert_result['label'] 
        bert_score = bert_result['score'] 
        
        stars = int(bert_label.split()[0]) 
        
        if stars >= 4:
            label = SentimentLabel.POSITIVE
            scores = {
                "positive": bert_score,
                "neutral": (1 - bert_score) * 0.3,  
                "negative": (1 - bert_score) * 0.1
            }
        
        elif stars == 3:
            label = SentimentLabel.NEUTRAL
            scores = {
                "positive": (1 - bert_score) * 0.3,
                "neutral": bert_score,
                "negative": (1 - bert_score) * 0.3
            }
        
        else:
            label = SentimentLabel.NEGATIVE
            scores = {
                "positive": (1 - bert_score) * 0.1,
                "neutral": (1 - bert_score) * 0.3,
                "negative": bert_score
            }
        
        total = sum(scores.values())
        scores = {k: v / total for k, v in scores.items()}
        
        return (label, bert_score, scores)
    
    def _truncate_text(self, text: str, max_tokens: int = 512) -> str:

        tokens = self.tokenizer.encode(
            text,
            add_special_tokens=True,
            max_length=max_tokens,
            truncation=True
        )
        
        truncated_text = self.tokenizer.decode(tokens, skip_special_tokens=True)
        
        return truncated_text
    
    def _analyze_sentiment_fallback(self, text: str) -> Tuple[SentimentLabel, float, Dict[str, float]]:

        text_lower = text.lower()
        
        positive_keywords = [
            "excelente", "bueno", "profesional", "recomiendo", "rápido",
            "calidad", "satisfecho", "genial", "perfecto", "confiable"
        ]
        
        negative_keywords = [
            "malo", "pésimo", "fraude", "robo", "caro", "lento",
            "no recomiendo", "decepcionado", "terrible", "incompetente"
        ]
        
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        
        if positive_count > negative_count:
            return (
                SentimentLabel.POSITIVE,
                0.7,  
                {"positive": 0.7, "neutral": 0.2, "negative": 0.1}
            )
        elif negative_count > positive_count:
            return (
                SentimentLabel.NEGATIVE,
                0.7,
                {"positive": 0.1, "neutral": 0.2, "negative": 0.7}
            )
        else:
            return self._create_neutral_response()
    
    def _create_neutral_response(self) -> Tuple[SentimentLabel, float, Dict[str, float]]:

        return (
            SentimentLabel.NEUTRAL,
            0.5,
            {"positive": 0.33, "neutral": 0.34, "negative": 0.33}
        )