import React, { useState } from 'react';
import { Button, Card, Form, Col, Row, Spinner } from 'react-bootstrap';
import axios from 'axios';
import { getReport } from './Services';
import { useAuth } from './AuthContext';

const SalesReport = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

	const auth = useAuth()

  const provinces = ["Province 1", "Province 2", "Province 3", "Province 4"]; // known province list

  const fetchSalesReport = async () => {
    setLoading(true);
    setError(null);

    try {
      // const response = await axios.get('https://api.example.com/sales-report', {
      //   params: {
      //     startDate,
      //     endDate,
      //   },
      // });
		const response = await getReport(auth, startDate, endDate);

      setReport(response.data);
    } catch (err) {
      setError('Failed to fetch report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchSalesReport();
  };

  return (
    <div className="container mt-5">
      <h2>Generate Sales Report</h2>
      <Form onSubmit={handleSubmit}>
        <Row className="mb-3">
          <Col md={6}>
            <Form.Group controlId="startDate">
              <Form.Label>Start Date</Form.Label>
              <Form.Control
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group controlId="endDate">
              <Form.Label>End Date</Form.Label>
              <Form.Control
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
            </Form.Group>
          </Col>
        </Row>
        <Button type="submit" variant="primary" disabled={loading}>
	  		Generuj raport
        </Button>
      </Form>

      {error && <div className="mt-3 text-danger">{error}</div>}

      {report && (
        <Card className="mt-4">
          <Card.Body>
            <Card.Title>Sales Report</Card.Title>
            <Card.Text><strong> Ilość zamówień </strong> {report.total_orders}</Card.Text>
            <Card.Text><strong> Suma zamówień </strong> ${report.total_sum.toFixed(2)}</Card.Text>

            <h5>Ilość zamówień w województwach:</h5>
            <ul>
              { Object.entries(report.orders_per_province).map(([province, cnt]) => {
                return (
                  <li key={province}>
                    {province}: {cnt}
                  </li>
                );
              })}
            </ul>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default SalesReport;
