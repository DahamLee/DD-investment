import { useEffect, useRef, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Chart } from 'react-chartjs-2'

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
)

export default function AdvancedCandlestickChart({ candles, indicators = [] }) {
  const chartRef = useRef()
  const [chartData, setChartData] = useState(null)

  useEffect(() => {
    if (candles && candles.length > 0) {
      prepareChartData()
    }
  }, [candles, indicators])

  function prepareChartData() {
    const labels = candles.map(candle => candle.date)
    
    // 캔들스틱을 위한 데이터 준비
    const candlestickData = candles.map(candle => ({
      x: candle.date,
      o: candle.open,
      h: candle.high,
      l: candle.low,
      c: candle.close,
      v: candle.volume
    }))

    // 종가 라인 (메인 라인)
    const closeData = candles.map(candle => candle.close)
    
    // 거래량 데이터
    const volumeData = candles.map(candle => candle.volume || 0)

    const datasets = [
      {
        label: '종가',
        data: closeData,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderWidth: 2,
        type: 'line',
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'y'
      }
    ]

    // 기술지표 추가
    if (indicators && indicators.length > 0) {
      // 이동평균선들
      if (indicators.some(ind => ind.ma5 !== null)) {
        datasets.push({
          label: 'MA5',
          data: indicators.map(ind => ind.ma5),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          borderWidth: 1,
          type: 'line',
          tension: 0.1,
          pointRadius: 0,
          yAxisID: 'y'
        })
      }

      if (indicators.some(ind => ind.ma20 !== null)) {
        datasets.push({
          label: 'MA20',
          data: indicators.map(ind => ind.ma20),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          borderWidth: 1,
          type: 'line',
          tension: 0.1,
          pointRadius: 0,
          yAxisID: 'y'
        })
      }

      if (indicators.some(ind => ind.ma60 !== null)) {
        datasets.push({
          label: 'MA60',
          data: indicators.map(ind => ind.ma60),
          borderColor: 'rgb(255, 206, 86)',
          backgroundColor: 'rgba(255, 206, 86, 0.1)',
          borderWidth: 1,
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
          data: indicators.map(ind => ind.bollinger_upper),
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
          data: indicators.map(ind => ind.bollinger_lower),
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
    plugins: {
      title: {
        display: true,
        text: '주식 차트 (종가 + 기술지표)'
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
            const label = context.dataset.label || ''
            const value = context.parsed.y
            if (value !== null) {
              return `${label}: ${value.toLocaleString()}원`
            }
            return ''
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: '날짜'
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
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
        <div>차트 데이터를 로딩 중...</div>
      </div>
    )
  }

  return (
    <div style={{ height: 400, width: '100%' }}>
      <Chart ref={chartRef} type="line" data={chartData} options={options} />
    </div>
  )
}

