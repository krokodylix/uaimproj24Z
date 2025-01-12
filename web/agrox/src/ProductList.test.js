import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ProductList from "./ProductList";
import { useAuth } from "./AuthContext";
import { getProducts, delProduct } from "./Services";
import { BrowserRouter as Router } from "react-router";

jest.mock("./Services", () => ({
  getProducts: jest.fn(),
}));

jest.mock("./AuthContext", () => ({
  useAuth: jest.fn(),
}));

describe("ProductList", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders product list correctly", async () => {
    const mockProducts = [
      { id: 1, image: "image1", description: "Product 1", price: "10" },
      { id: 2, image: "image2", description: "Product 2", price: "20" },
    ];
    useAuth.mockReturnValue({ is_admin: () => false });
    getProducts.mockResolvedValue({ data: mockProducts });
    render(
      <Router>
        <ProductList />
      </Router>
    );
    await waitFor(() => {
      expect(screen.getByText("Produkt 1")).toBeInTheDocument();
      expect(screen.getByText("Produkt 2")).toBeInTheDocument();
    });
  });


  it('shows "Edytuj" button for admins', async () => {
    const mockProduct = { id: 1, image: "image1", description: "Product 1", price: "10" };
    useAuth.mockReturnValue({ is_admin: () => true });
    getProducts.mockResolvedValue({ data: [mockProduct] });
    render(
      <Router>
        <ProductList />
      </Router>
    );
    await waitFor(() => {
      expect(screen.getByText("Edytuj")).toBeInTheDocument();
    });
  });
});
