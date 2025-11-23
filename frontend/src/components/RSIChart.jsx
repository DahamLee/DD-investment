import { useEffect, useRef, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
)

export default function RSIChart({ indicators = [] }) {
  const [chartData, setChartData] = useState(null)

  useEffect(() => {
    if (indicators && indicators.length > 0) {
      prepareChartData()
    }
  }, [indicators])

  function prepareChartData() {
    const labels = indicators.map(ind => ind.date)
    const rsiData = indicators.map(ind => ind.rsi)
    const macdData = indicators.map(ind => ind.macd)
    const macdSignalData = indicators.map(ind => ind.macd_signal)

    const datasets = []

    // RSI 데이터
    if (rsiData.some(val => val !== null)) {
      datasets.push({
        label: 'RSI',
        data: rsiData,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 2,
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'rsi'
      })
    }

    // MACD 데이터
    if (macdData.some(val => val !== null)) {
      datasets.push({
        label: 'MACD',
        data: macdData,
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        borderWidth: 2,
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'macd'
      })
    }

    if (macdSignalData.some(val => val !== null)) {
      datasets.push({
        label: 'MACD Signal',
        data: macdSignalData,
        borderColor: 'rgb(255, 206, 86)',
        backgroundColor: 'rgba(255, 206, 86, 0.1)',
        borderWidth: 2,
        tension: 0.1,
        pointRadius: 0,
        yAxisID: 'macd'
      })
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
        text: 'RSI & MACD 지표'
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
              return `${label}: ${value.toFixed(2)}`
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
      rsi: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'RSI'
        },
        min: 0,
        max: 100,
        ticks: {
          callback: function(value) {
            return value.toFixed(0)
          }
        },
        grid: {
          drawOnChartArea: true,
        }
      },
      macd: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'MACD'
        },
        ticks: {
          callback: function(value) {
            return value.toFixed(2)
          }
        },
        grid: {
          drawOnChartArea: false,
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
        height: 300, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        border: '1px solid #eee',
        borderRadius: 8,
        background: '#f9f9f9'
      }}>
        <div>RSI 차트 데이터를 로딩 중...</div>
      </div>
    )
  }

  return (
    <div style={{ height: 300, width: '100%' }}>
      <Line data={chartData} options={options} />
    </div>
  )
}

