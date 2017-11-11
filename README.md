# textsum-textrank

结果展示
https://github.com/Samurais/conv_seq2seq_gateway/tree/master/client_extract

<img width="884" alt="screen shot 2017-11-09 at 6 18 32 pm" src="https://user-images.githubusercontent.com/3538629/32600390-1477a3b8-c505-11e7-9ce3-e758169e6793.png">


<img width="825" alt="screen shot 2017-11-09 at 6 19 02 pm" src="https://user-images.githubusercontent.com/3538629/32600412-24fc2a1a-c505-11e7-8d3a-b86b1298f3eb.png">

## Usage

src/summarizer.py
```
sm = summarizer.Summarizer
abstract, scores = sm.extract(content, title)
```

## Demo

```
scripts/client.start.sh
```

