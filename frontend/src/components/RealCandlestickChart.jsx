import { useEffect, useRef, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Chart } from 'react-chartjs-2'
import { CandlestickController, CandlestickElement } from 'chartjs-chart-financial'

// Date adapter import
import 'chartjs-adapter-date-fns'

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  CandlestickController,
  CandlestickElement
)

export default function RealCandlestickChart({ candles, indicators = [] }) {
  const chartRef = useRef()
  const [chartData, setChartData] = useState(null)

  useEffect(() => {
    if (candles && candles.length > 0) {
      prepareChartData()
    }
  }, [candles, indicators])

  function prepareChartData() {
    // 캔들 데이터를 financial 차트 형식으로 변환
    const labels = candles.map(candle => candle.date)
    const candlestickData = candles.map(candle => ({
      x: candle.date, // 날짜 문자열로 사용
      o: candle.open,
      h: candle.high,
      l: candle.low,
      c: candle.close,
      v: candle.volume || 0
    }))

    const datasets = [
      {
        label: 'OHLC',
        data: candlestickData,
        type: 'candlestick',
        borderColor: {
          up: '#26a69a',    // 상승 캔들 색상
          down: '#ef5350',  // 하락 캔들 색상
          unchanged: '#999' // 보합 캔들 색상
        },
        backgroundColor: {
          up: 'rgba(38, 166, 154, 0.1)',
          down: 'rgba(239, 83, 80, 0.1)',
          unchanged: 'rgba(153, 153, 153, 0.1)'
        },
        // 캔들 너비 조정
        barPercentage: 0.6,
        categoryPercentage: 0.6,
        // 캔들 간격 설정
        maxBarThickness: 20
      }
    ]

    // 기술지표 추가
    if (indicators && indicators.length > 0) {
      // 이동평균선들
      if (indicators.some(ind => ind.ma5 !== null)) {
        datasets.push({
          label: 'MA5',
          data: indicators.map(ind => ({
            x: ind.date,
            y: ind.ma5
          })).filter(item => item.y !== null),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          borderWidth: 2,
          type: 'line',
          tension: 0.1,
          pointRadius: 0,
          yAxisID: 'y'
        })
      }

      if (indicators.some(ind => ind.ma20 !== null)) {
        datasets.push({
          label: 'MA20',
          data: indicators.map(ind => ({
            x: ind.date,
            y: ind.ma20
          })).filter(item => item.y !== null),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          borderWidth: 2,
          type: 'line',
          tension: 0.1,
          pointRadius: 0,
          yAxisID: 'y'
        })
      }

      if (indicators.some(ind => ind.ma60 !== null)) {
        datasets.push({
          label: 'MA60',
          data: indicators.map(ind => ({
            x: ind.date,
            y: ind.ma60
          })).filter(item => item.y !== null),
          borderColor: 'rgb(255, 206, 86)',
          backgroundColor: 'rgba(255, 206, 86, 0.1)',
          borderWidth: 2,
          type: 'line',
          tension: 0.1,
          pointRadius: 0,
          yAxisID: 'y'
        })
      }

      // 볼린저 밴드
      if (indicators.some(ind => ind.bollinger_upper !== null)) {
        datasets.push({
          label: '볼린저 상단',
          data: indicators.map(ind => ({
            x: ind.date,
            y: ind.bollinger_upper
          })).filter(item => item.y !== null),
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.1)',
          borderWidth: 1,
          type: 'line',
          tension: 0.1,
          pointRadius: 0,
          yAxisID: 'y',
          borderDash: [5, 5]
        })
      }

      if (indicators.some(ind => ind.bollinger_lower !== null)) {
        datasets.push({
          label: '볼린저 하단',
          data: indicators.map(ind => ({
            x: ind.date,
            y: ind.bollinger_lower
          })).filter(item => item.y !== null),
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.1)',
          borderWidth: 1,
          type: 'line',
          tension: 0.1,
          pointRadius: 0,
          yAxisID: 'y',
          borderDash: [5, 5]
        })
      }
    }

    setChartData({
      labels,
      datasets
    })
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    // 캔들 간격 조정
    layout: {
      padding: {
        left: 10,
        right: 10,
        top: 10,
        bottom: 10
      }
    },
    plugins: {
      title: {
        display: true,
        text: '주식 캔들스틱 차트'
      },
      legend: {
        display: true,
        position: 'top'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: function(context) {
            if (context.dataset.type === 'candlestick') {
              const data = context.raw
              return [
                `시가: ${data.o.toLocaleString()}원`,
                `고가: ${data.h.toLocaleString()}원`,
                `저가: ${data.l.toLocaleString()}원`,
                `종가: ${data.c.toLocaleString()}원`,
                `거래량: ${data.v.toLocaleString()}`
              ]
            } else {
              const label = context.dataset.label || ''
              const value = context.parsed.y
              return `${label}: ${value.toLocaleString()}원`
            }
          }
        }
      }
    },
    scales: {
      x: {
        type: 'category',
        title: {
          display: true,
          text: '날짜'
        },
        // 캔들 간격 조정
        offset: true,
        grid: {
          offset: true
        }
      },
      y: {
        type: 'linear',
        display: true,
        title: {
          display: true,
          text: '가격 (원)'
        },
        ticks: {
          callback: function(value) {
            return value.toLocaleString()
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  }

  if (!chartData) {
    return (
      <div style={{ 
        height: 400, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        border: '1px solid #eee',
        borderRadius: 8,
        background: '#f9f9f9'
      }}>
        <div>캔들스틱 차트 데이터를 로딩 중...</div>
      </div>
    )
  }

  return (
    <div style={{ height: 400, width: '100%' }}>
      <Chart ref={chartRef} type="candlestick" data={chartData} options={options} />
    </div>
  )
}
